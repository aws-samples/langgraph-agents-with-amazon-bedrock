"""Track 2 - LangGraph agent with PII masking (defense in depth).

Pipeline:  mask_input (Comprehend) -> call_agent (Guardrail-attached model) -> scrub_output (Guardrail)

Two independent controls at two boundaries:
  - App layer:   Amazon Comprehend masks PII before the prompt is built.
  - Model layer: a Bedrock Guardrail anonymizes/blocks PII on input and output.

Deployable on AgentCore Runtime (same BedrockAgentCoreApp wrapper as Track 1).
"""

import os
from typing import TypedDict

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from langchain_aws import ChatBedrockConverse
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import create_react_agent

from pii import comprehend_mask, guardrail_apply

REGION = os.getenv("AWS_REGION", "us-east-1")
MODEL_ID = os.getenv("MODEL_ID", "us.amazon.nova-pro-v1:0")
GUARDRAIL_ID = os.getenv("GUARDRAIL_ID")
GUARDRAIL_VERSION = os.getenv("GUARDRAIL_VERSION", "DRAFT")


@tool
def get_order_status(order_id: str) -> str:
    """Look up the delivery status of a customer order by its ID."""
    return f"Order {order_id} has shipped and arrives in 2 days."


def _model():
    kwargs = {"model": MODEL_ID, "region_name": REGION}
    if GUARDRAIL_ID:
        # Model-layer guardrail via the Converse guardrailConfig. Confirm the exact
        # parameter name against your installed langchain-aws version.
        kwargs["guardrail_config"] = {
            "guardrailIdentifier": GUARDRAIL_ID,
            "guardrailVersion": GUARDRAIL_VERSION,
            "trace": "enabled",
        }
    return ChatBedrockConverse(**kwargs)


_agent = create_react_agent(
    _model(), tools=[get_order_status],
    prompt="You are a concise customer-support agent.",
)


class State(TypedDict):
    prompt: str
    masked_prompt: str
    answer: str
    safe_answer: str


def mask_input(state: State) -> dict:
    """App-layer: deterministically mask PII in the user's prompt."""
    masked, _entities = comprehend_mask(state["prompt"])
    return {"masked_prompt": masked}


def call_agent(state: State) -> dict:
    """Run the agent on the masked prompt (model also has the guardrail attached)."""
    result = _agent.invoke({"messages": [("user", state["masked_prompt"])]})
    return {"answer": result["messages"][-1].content}


def scrub_output(state: State) -> dict:
    """Belt-and-suspenders: guardrail + deterministic masking on the way out."""
    safe, _ = guardrail_apply(
        state["answer"], GUARDRAIL_ID, GUARDRAIL_VERSION, source="OUTPUT"
    )
    safe, _ = comprehend_mask(safe)
    return {"safe_answer": safe}


def build_graph():
    g = StateGraph(State)
    g.add_node("mask_input", mask_input)
    g.add_node("call_agent", call_agent)
    g.add_node("scrub_output", scrub_output)
    g.add_edge(START, "mask_input")
    g.add_edge("mask_input", "call_agent")
    g.add_edge("call_agent", "scrub_output")
    g.add_edge("scrub_output", END)
    return g.compile()


graph = build_graph()
app = BedrockAgentCoreApp()


@app.entrypoint
def invoke(payload, context):
    prompt = payload.get("prompt", "")
    out = graph.invoke({"prompt": prompt})
    return {"result": out["safe_answer"], "masked_prompt": out.get("masked_prompt", "")}


if __name__ == "__main__":
    app.run()
