"""Track 3 - LangGraph agent consuming AgentCore Gateway tools over MCP.

Uses `langchain-mcp-adapters` to load the Gateway's MCP tools into a LangGraph agent. The
Gateway aggregates backend targets (Lambda / OpenAPI / API Gateway / internal MCP servers)
behind a single authenticated MCP URL, so the agent only speaks MCP.

Deployable on AgentCore Runtime (async entrypoint).
"""

import os

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from langchain_aws import ChatBedrockConverse
from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

from mcp_oauth import GATEWAY_MCP_URL, get_oauth_token

REGION = os.getenv("AWS_REGION", "us-east-1")
MODEL_ID = os.getenv("MODEL_ID", "us.amazon.nova-pro-v1:0")


@tool
def whoami() -> str:
    """Return which agent is serving the request (a local, in-process tool)."""
    return "LangGraph agent on AgentCore Runtime, us-east-1."


def _mcp_client():
    """Build an MCP client pointed at the Gateway, authenticated with a bearer token."""
    token = get_oauth_token()
    return MultiServerMCPClient(
        {
            "agentcore_gateway": {
                "url": GATEWAY_MCP_URL,
                "transport": "streamable_http",
                "headers": {"Authorization": f"Bearer {token}"},
            }
        }
    )


app = BedrockAgentCoreApp()


@app.entrypoint
async def invoke(payload, context):
    # Discover remote tools exposed by the Gateway, then combine with local tools.
    gateway_tools = await _mcp_client().get_tools()
    model = ChatBedrockConverse(model=MODEL_ID, region_name=REGION)
    agent = create_react_agent(
        model,
        tools=[whoami] + gateway_tools,
        prompt=(
            "You are a support agent. Use the gateway tools to access internal "
            "systems (e.g. order lookups via the internal API)."
        ),
    )
    result = await agent.ainvoke({"messages": [("user", payload.get("prompt", ""))]})
    return {"result": result["messages"][-1].content}


if __name__ == "__main__":
    app.run()
