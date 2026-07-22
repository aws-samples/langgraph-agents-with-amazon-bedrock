# Track 3 — MCP Server + AgentCore Gateway to Internal GraphQL APIs

Give the agent a **secure, governed tool channel** to internal systems. The customer's target is
agentic access to **internal GraphQL APIs running on EC2**.

Scope (as agreed): the **internal-GraphQL-on-EC2** path is taught as **architecture + demo**, while
a **general AgentCore Gateway lab is hands-on** and aligned with this codebase — participants build
a Gateway, expose a tool, and call it from the LangGraph agent over MCP.

## Objectives

1. Understand MCP as the standard agent-to-tool interface, and what **AgentCore Gateway** adds
   (one authenticated MCP endpoint in front of many backends).
2. **Hands-on:** create a Gateway, add a **Lambda target**, and consume its tools from LangGraph
   via `langchain-mcp-adapters`.
3. Manage **secrets** with Secrets Manager / AgentCore credential providers — never hardcoded.
4. **Architect** private connectivity to an internal GraphQL API on EC2 (VPC, no public internet).

## Files

| File | Purpose |
|---|---|
| `mcp_oauth.py` | Cognito client-credentials OAuth token for the Gateway MCP URL (framework-agnostic) |
| `agent_mcp.py` | LangGraph agent that loads Gateway MCP tools via `langchain-mcp-adapters` (AgentCore-deployable) |
| `lambda_target.py` | Example Gateway **Lambda target** (`get_order_status` + an internal-GraphQL bridge) |
| `order_tool_schema.json` | `inlinePayload` tool schema registered with the Lambda target |

## Concepts

AgentCore Gateway is a **managed MCP endpoint**. It fronts multiple **target** types — Lambda,
OpenAPI, Smithy, **API Gateway REST**, and **existing MCP servers** — and presents them to agents as
one MCP URL. **Inbound** access is OAuth2 (Cognito) / IAM; **outbound** credentials to backends are
managed via execution roles or AgentCore **credential providers**.

```
LangGraph agent ──(OAuth2 bearer)──> AgentCore Gateway (MCP) ──> Lambda / OpenAPI / API GW / MCP
```

---

## Part A — Hands-on: Gateway + Lambda target + LangGraph

### A1. Deploy the Lambda target

Package `lambda_target.py` as a Lambda in `us-east-1` (handler `lambda_target.lambda_handler`).
Note its ARN and put it in `order_tool_schema.json`.

### A2. Create the Gateway and add the target

```bash
agentcore gateway create-mcp-gateway --name SupportGateway --region us-east-1
# Save the output: gateway ARN, gateway URL, role ARN, Cognito client id/secret, token endpoint

agentcore gateway create-mcp-gateway-target \
  --gateway-arn  <gateway-arn> \
  --gateway-url  <gateway-url> \
  --role-arn     <role-arn> \
  --name OrderTools \
  --target-type lambda \
  --target-payload "$(cat order_tool_schema.json)" \
  --region us-east-1
```

> Subcommand names follow the current AgentCore Gateway CLI; confirm with `agentcore gateway --help`
> at delivery. Targets can also be created in the console or via the control-plane API.

### A3. Point the agent at the Gateway

```bash
cd session-2-advanced/track-3-mcp-gateway
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

export GATEWAY_MCP_URL=<gateway-url>/mcp
export GATEWAY_CLIENT_ID=<cognito-client-id>
export GATEWAY_CLIENT_SECRET=<cognito-client-secret>
export GATEWAY_TOKEN_ENDPOINT=<cognito-domain>/oauth2/token
export GATEWAY_SCOPE=SupportGateway/invoke

python agent_mcp.py
agentcore invoke --dev '{"prompt": "What is the status of order 35476?"}'
```

The agent fetches a bearer token, lists the Gateway's MCP tools (your Lambda's
`get_order_status`), and calls it — all over MCP. The agent code never imports the Lambda; it only
speaks MCP. Swapping or adding backends doesn't change the agent.

---

## Part B — Architecture/demo: reaching the internal GraphQL on EC2

The customer's GraphQL API is **private** (EC2 in a VPC). Two production-grade patterns:

**Pattern 1 — Lambda-in-VPC bridge (used by `lambda_target.py::query_internal_graphql`)**
```
Agent ─OAuth─> Gateway ─> Lambda (VPC-attached) ─private─> GraphQL on EC2
                                   │
                                   └─ token from Secrets Manager (not hardcoded)
```
The Lambda runs in the customer VPC/subnets, calls the private GraphQL endpoint over the VPC, and
reads the endpoint token from Secrets Manager. Nothing is exposed to the public internet.

**Pattern 2 — Gateway VPC egress (VPC Lattice)**
For OpenAPI / MCP-server / API Gateway targets that live in a VPC, AgentCore Gateway supports
**VPC egress via Amazon VPC Lattice** private endpoints, routing securely without public exposure.
For MCP servers hosted on AgentCore Runtime/Gateway, traffic stays on the AWS backbone. OAuth
client-credentials is the recommended production auth.

> Note: the `API_GATEWAY` target type requires a **public** REST API. For a **private** internal
> API, use Pattern 1 (Lambda-in-VPC) or Pattern 2 (VPC Lattice egress).

### Secrets & identity

- Store the GraphQL token/credentials in **AWS Secrets Manager**; grant the Lambda (or Gateway
  execution role) read access to just that secret.
- For per-user / delegated access to the backend, use **AgentCore Identity** outbound credential
  providers (OAuth2) instead of a shared static token.

### MCP-server-on-AgentCore option

Instead of a Lambda target, you can host your own **MCP server** (Python tools that wrap GraphQL)
on **AgentCore Runtime** and register it as an MCP target. An AgentCore-hosted MCP server keeps
traffic on the AWS backbone. The tool code is the `query_internal_graphql` logic, exposed as MCP.

---

## Security notes (for the Security Engineers)

- One **authenticated** entry point (OAuth2/IAM) instead of N ad-hoc API keys in the agent.
- **No hardcoded secrets** — Secrets Manager / AgentCore credential providers; least-privilege role.
- **No public internet** for the internal API — VPC-attached Lambda or VPC Lattice egress.
- Gateway calls are logged to **CloudTrail / CloudWatch** for audit.
- Apply **least-privilege** tool schemas — expose only the GraphQL operations agents should use
  (e.g., read-only queries), not the whole API.

## Residency

Gateway, Lambda, Secrets Manager, and the EC2 GraphQL all run in `us-east-1`; model calls use the US
CRIS profile. The tool channel keeps internal data within the US. See Track 4.

## Teardown

```bash
agentcore gateway delete-mcp-gateway --name SupportGateway --force --region us-east-1
# delete the Lambda, its VPC config, and the Secrets Manager secret
```

## How this maps to the customer ask

> "MCP Server: Python functions/secrets in AgentCore, interfacing agentic AI with internal GraphQL
> APIs on EC2."

- **Python functions as MCP tools** -> Lambda target / AgentCore-hosted MCP server (`lambda_target.py`)
- **Secrets** -> Secrets Manager + AgentCore Identity (no hardcoding)
- **Internal GraphQL on EC2** -> VPC-attached Lambda bridge or VPC Lattice egress (architecture)
- **Consumed by the agent** -> `langchain-mcp-adapters` in `agent_mcp.py`

**Status:** authored. Confirm at delivery: exact `agentcore gateway` subcommands, the
`langchain-mcp-adapters` version/API, and the Gateway->Lambda invocation contract.
