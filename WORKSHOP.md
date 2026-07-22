# Workshop: Agentic AI on AWS — LangGraph + Amazon Bedrock AgentCore

A two-session, hands-on workshop. **Session 1** builds foundational agentic systems with
**LangGraph** (the labs in this repo). **Session 2** continues by deploying and hardening those
agents on **Amazon Bedrock AgentCore**, with a strong focus on **security, privacy, and US data
residency**.

> Region: **us-east-1 (N. Virginia)** · Delivery: **customer AWS accounts** (~15 participants) ·
> Models: **Amazon Nova Pro on Amazon Bedrock via US cross-region inference (CRIS)**

This file is the workshop overview. For the original DeepLearning.AI foundation setup, see
[`README.md`](./README.md).

---

## Who this is for

| Session | Level | Audience | Focus |
|---|---|---|---|
| **Session 1** | Foundational / Intermediate | Software Engineers new to building apps with LLMs | Building **agentic systems** with LangGraph (explicitly **not** RAG) |
| **Session 2** | Advanced | Software + ML + **Security** Engineers | Production deployment on AgentCore, PII protection, internal API access via MCP, and Amazon Nova data residency |

## What participants build

```
Session 1  ──>  a working LangGraph agent (tools, state, persistence, HITL, multi-agent)
                          │
Session 2  ──>  the same agent, deployed & hardened on AWS:
                ├─ Track 1  AgentCore Runtime + Sessions + Memory + Observability
                ├─ Track 2  PII Masker (Bedrock Guardrails + Amazon Comprehend)
                ├─ Track 3  MCP server + AgentCore Gateway -> internal GraphQL on EC2
                └─ Track 4  Privacy, Data Security & Data Residency for Amazon Nova (US)
```

One agent, taken from "runs on my laptop" (Session 1) to "deployed, observable, private, and
integrated with internal systems — inside the US" (Session 2).

---

## Repository layout

```
langgraph-agents-with-amazon-bedrock/
├── README.md                  original foundation setup (DeepLearning.AI course)
├── WORKSHOP.md                this file — the 2-session overview
├── Lab_1 .. Lab_6/            SESSION 1 foundation labs
├── utils/  assets/            shared by the Session 1 labs
├── session-1-foundations/     Session 1 framing + US retargeting guide
├── session-2-advanced/        SESSION 2 — AgentCore continuation
│   ├── track-1-agentcore-runtime/
│   ├── track-2-pii-masker/
│   ├── track-3-mcp-gateway/
│   └── track-4-privacy-data-residency/
└── bootstrap/                 customer-account setup (IAM, CloudFormation, pre-flight, teardown)
```

## Session 1 — Foundations (this repo's labs)

Build agentic systems with LangGraph. Reuses **[`Lab_1`](./Lab_1/) … [`Lab_6`](./Lab_6/)**, framed
and retargeted for this workshop (us-east-1 region, US model IDs, agent-centric framing — not RAG).

- Framing + objectives: [`session-1-foundations/README.md`](./session-1-foundations/README.md)
- Apply the US changes: [`session-1-foundations/RETARGETING.md`](./session-1-foundations/RETARGETING.md)
- Original environment setup: [`README.md`](./README.md)

## Session 2 — Advanced (AgentCore continuation)

Take the Session 1 agent to production. See [`session-2-advanced/README.md`](./session-2-advanced/README.md).

| Track | Title | AWS services |
|---|---|---|
| [1](./session-2-advanced/track-1-agentcore-runtime/) | Agents on AgentCore (Runtime/Sessions/Memory/Observability) | Bedrock AgentCore, CloudWatch |
| [2](./session-2-advanced/track-2-pii-masker/) | PII Masker | Bedrock Guardrails, Amazon Comprehend |
| [3](./session-2-advanced/track-3-mcp-gateway/) | MCP server + Gateway -> internal GraphQL on EC2 | AgentCore Gateway, Secrets Manager, VPC/PrivateLink |
| [4](./session-2-advanced/track-4-privacy-data-residency/) | Privacy & Data Residency for Amazon Nova | Bedrock US CRIS, SCP data perimeter |

---

## Region & model strategy (US residency)

- **Source region for all labs: `us-east-1`.**
- Models are invoked through **US geographic cross-region inference profiles** (the `us.` prefix),
  which keep inference within US Regions. This satisfies the data-residency requirement.
- Default model IDs (validated during the pre-flight in `bootstrap/`):
  - `us.amazon.nova-lite-v1:0` — fast / cost-efficient default
  - `us.amazon.nova-pro-v1:0` — reasoning / harder agent steps (and the Session 2 tracks)

## Prerequisites

- **Session 1:** follow the foundation setup in [`README.md`](./README.md), then apply
  [`session-1-foundations/RETARGETING.md`](./session-1-foundations/RETARGETING.md) (region + US model IDs).
- **Session 2:** complete the [`bootstrap/`](./bootstrap/) pre-flight (region, model access in
  `us-east-1`, IAM, Docker, AgentCore CLI) in each participant's customer account.

## Suggested schedule

| Block | Content | Approx. time |
|---|---|---|
| Session 1 | Foundations (LangGraph agentic systems, Labs 1–6) | ~2.5–3 h |
| Session 2 · Track 1 | Deploy to AgentCore (Runtime/Sessions/Memory/Observability) | ~60 min |
| Session 2 · Track 2 | PII Masker (Guardrails + Comprehend) | ~45 min |
| Session 2 · Track 3 | MCP server + Gateway -> internal GraphQL | ~60 min |
| Session 2 · Track 4 | Privacy, Data Security & Data Residency | ~30–45 min (theory + demo) |

## Build status

- [x] Design & overview (this file)
- [x] Session 1 — foundation labs (existing) + US retargeting guide
- [x] Session 2 · Track 1 — AgentCore Runtime (agent + memory + guided lab)
- [x] Session 2 · Track 2 — PII Masker (Comprehend + Guardrails, LangGraph nodes)
- [x] Session 2 · Track 3 — MCP + Gateway (hands-on Lambda target + internal-GraphQL architecture)
- [x] Session 2 · Track 4 — Privacy & data residency (US CRIS demo + data-perimeter SCP)
- [x] Bootstrap — IAM policy, CloudFormation, pre-flight, cost, teardown

## Key references (verified during design)

- Geographic cross-Region inference — <https://docs.aws.amazon.com/bedrock/latest/userguide/geographic-cross-region-inference.html>
- Unlocking AI flexibility in Europe (US CRIS guide) — AWS ML Blog
- Models & Regions compatibility — <https://docs.aws.amazon.com/bedrock/latest/userguide/models-region-compatibility.html>
- Data perimeter for Amazon Bedrock (SCP regional boundary enforcement) — AWS Prescriptive Guidance
- Amazon Bedrock AgentCore — getting started / runtime / memory / gateway

> Content adapted from AWS documentation; verify model IDs, region availability, and the exact
> AgentCore CLI surface against the live console during the pre-flight, as the Bedrock/AgentCore
> surface evolves quickly.
