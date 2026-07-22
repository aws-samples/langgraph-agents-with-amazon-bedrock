# Session 2 — Advanced: Production, Security & Internal Integration

**Audience:** Software Engineers + Machine Learning Engineers + **Security Engineers**.
**Focus:** Take the Session 1 LangGraph agent and make it production-grade on AWS — deployed,
observable, privacy-preserving, integrated with internal systems, and US-resident.

Security and privacy are the through-line: three of the four tracks are security-driven, which
matches the audience.

## The four tracks (customer-requested)

| Track | Title | What it delivers | Core AWS services |
|---|---|---|---|
| **1** | Agents on AgentCore | Deploy the LangGraph agent with **sessions, memory, observability** | Bedrock AgentCore (Runtime, Memory, Observability), CloudWatch |
| **2** | PII Masker | **PII detection, Guardrails, masking** in the agent request/response path | Bedrock Guardrails, Amazon Comprehend |
| **3** | MCP server + Gateway | An **MCP server of Python tools** that reaches **internal GraphQL APIs on EC2**, with secrets | AgentCore Gateway, Secrets Manager / AgentCore Identity, VPC/PrivateLink, EC2 |
| **4** | Privacy & Data Residency | **Data residency for Amazon Nova** + data-security posture | Bedrock US CRIS, VPC endpoints, SCP data perimeter |

## How the tracks build on each other

```
Track 1 (deployed agent)
   ├─ Track 2 wraps its model calls with PII masking + Guardrails
   ├─ Track 3 gives it a secure tool channel to internal APIs (MCP + Gateway)
   └─ Track 4 explains/enforces where all of the above runs and stores data (US)
```

Track 1 is the foundation — build it first. Tracks 2–4 can be taught in any order after it.

## Per-track detail

- [`track-1-agentcore-runtime/`](./track-1-agentcore-runtime/)
- [`track-2-pii-masker/`](./track-2-pii-masker/)
- [`track-3-mcp-gateway/`](./track-3-mcp-gateway/)
- [`track-4-privacy-data-residency/`](./track-4-privacy-data-residency/)

**Status:** scaffold — tracks authored in tasks #4–#7.
