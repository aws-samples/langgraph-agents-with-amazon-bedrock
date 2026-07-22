"""Track 1 - A LangGraph agent wrapped for Amazon Bedrock AgentCore Runtime.

This is the Session 1 agent (a tool-using LangGraph agent) made deployable on
AgentCore Runtime with session isolation and optional AgentCore Memory.

Runtime contract (handled by BedrockAgentCoreApp): the container serves
`/invocations` and `/ping` on port 8080. Locally, `app.run()` starts that server.

Region/residency: inference uses a US geographic cross-region inference profile
(the `us.` prefix), which keeps processing within US Regions. See Track 4.
"""

import os

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from langchain_aws import ChatBedrockConverse
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

# Optional AgentCore Memory wiring. These are no-ops until a memory resource is
# configured (see the lab README, Step 3), so the agent deploys cleanly first.
from memory import load_context, save_turns

REGION = os.getenv("AWS_REGION", "us-east-1")
# US CRIS profile -> inference stays within the US geography.
MODEL_ID = os.getenv("MODEL_ID", "us.amazon.nova-pro-v1:0")

SYSTEM_PROMPT = (
    "You are a concise customer-support agent. "
    "Use tools when they help. If earlier context is provided under 'Relevant "
    "memory', use it to personalize your answer."
)


@tool
def get_order_status(order_id: str) -> str:
    """Look up the delivery status of a customer order by its ID."""
    # Demo stub. In Track 3 this is replaced by a real call to an internal
    # GraphQL API via an MCP tool / AgentCore Gateway.
    return f"Order {order_id} has shipped and is expected to arrive in 2 days."


def build_agent():
    """Build the LangGraph ReAct agent (the artifact carried from Session 1)."""
    model = ChatBedrockConverse(model=MODEL_ID, region_name=REGION)
    return create_react_agent(model, tools=[get_order_status], prompt=SYSTEM_PROMPT)


agent = build_agent()
app = BedrockAgentCoreApp()


@app.entrypoint
def invoke(payload, context):
    """AgentCore Runtime entrypoint.

    `payload` is the JSON request body; `context` carries session metadata
    (session_id, user_id) used for isolation and memory scoping.
    """
    prompt = payload.get("prompt", "")
    session_id = getattr(context, "session_id", "default-session")
    actor_id = getattr(context, "user_id", "default-user")

    # Durable cross-session context from AgentCore Memory (empty if not enabled).
    memory_context = load_context(actor_id, session_id, query=prompt)

    messages = []
    if memory_context:
        messages.append(("system", f"Relevant memory:\n{memory_context}"))
    messages.append(("user", prompt))

    result = agent.invoke({"messages": messages})
    answer = result["messages"][-1].content

    # Persist the turn (short-term + long-term extraction). No-op if not enabled.
    save_turns(actor_id, session_id, user_text=prompt, assistant_text=answer)

    return {"result": answer}


if __name__ == "__main__":
    # Starts the local AgentCore-compatible server on :8080 for `agentcore invoke`.
    app.run()
