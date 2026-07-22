"""Example AgentCore Gateway *Lambda target*.

Gateway exposes this Lambda's tools as MCP tools (no public endpoint of your own needed).
In the hands-on lab it implements `get_order_status`. The SAME pattern bridges to an
INTERNAL GraphQL API on EC2: deploy this Lambda inside the customer VPC and have it call the
private GraphQL endpoint, reading the endpoint token from Secrets Manager (never hardcoded).
See the README architecture section for the private-networking path.

Invocation contract: AgentCore Gateway invokes the target Lambda with the tool arguments as
the event; the tool name is provided via the Lambda client context. Exact keys can vary by
release - confirm against current docs at delivery.
"""

import json
import os
import urllib.request

import boto3


def _tool_name(context):
    cc = getattr(context, "client_context", None)
    if cc and getattr(cc, "custom", None):
        return cc.custom.get("bedrockAgentCoreToolName")
    return None


def get_order_status(arguments):
    """Demo tool: returns a canned order status."""
    order_id = arguments.get("order_id", "unknown")
    return {"order_id": order_id, "status": "shipped", "eta_days": 2}


def query_internal_graphql(arguments):
    """Bridge to a private GraphQL API on EC2 using a secret token from Secrets Manager.

    Network path (README): this Lambda is VPC-attached; the GraphQL endpoint is private
    (EC2 in the same VPC). Traffic stays off the public internet.
    """
    region = os.environ.get("AWS_REGION", "us-east-1")
    secret_name = os.environ.get("GRAPHQL_SECRET_NAME", "internal/graphql/token")
    endpoint = os.environ.get("GRAPHQL_ENDPOINT", "http://graphql.internal.local/graphql")

    sm = boto3.client("secretsmanager", region_name=region)
    token = sm.get_secret_value(SecretId=secret_name)["SecretString"]

    body = json.dumps({"query": arguments.get("query", "")}).encode()
    req = urllib.request.Request(
        endpoint,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )
    with urllib.request.urlopen(req, timeout=10) as resp:  # nosec B310 - private VPC endpoint
        return json.loads(resp.read().decode())


TOOLS = {
    "get_order_status": get_order_status,
    "query_internal_graphql": query_internal_graphql,
}


def lambda_handler(event, context):
    name = _tool_name(context) or event.get("tool_name", "get_order_status")
    arguments = event.get("arguments", event)
    fn = TOOLS.get(name)
    if not fn:
        return {"error": f"Unknown tool: {name}"}
    return fn(arguments)
