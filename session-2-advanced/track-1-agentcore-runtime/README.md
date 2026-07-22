# Track 1 — Deploy a LangGraph Agent to Amazon Bedrock AgentCore

Take the Session 1 LangGraph agent from "runs on my laptop" to a **serverless, session-isolated,
observable, memory-backed** deployment on **AgentCore Runtime** — in **us-east-1 (N. Virginia)**.

AgentCore is framework-agnostic and officially supports LangGraph, so the agent code does not get
rewritten — it gets **wrapped**.

## Objectives

1. Wrap a LangGraph agent as an AgentCore Runtime entrypoint and deploy it.
2. Use **session isolation** so each conversation is independent.
3. Add **AgentCore Memory** — short-term turns + long-term extracted facts.
4. Turn on **Observability** and read traces/metrics in CloudWatch.

## Files

| File | Purpose |
|---|---|
| `agent.py` | LangGraph ReAct agent wrapped with `BedrockAgentCoreApp` + `@app.entrypoint` |
| `memory.py` | Optional, framework-agnostic AgentCore Memory wiring (no-op until enabled) |
| `requirements.txt` | `bedrock-agentcore`, `langgraph`, `langchain-aws`, `langchain-core` |

## Prerequisites

Complete the [`bootstrap/`](../../bootstrap/) pre-flight first (region, model access in
`us-east-1`, IAM, Docker, AgentCore CLI). Confirm `aws sts get-caller-identity` resolves to the
intended **customer account**.

> **Tooling note (read once):** AgentCore's CLI is evolving and you may encounter two variants —
> the unified `@aws/agentcore` CLI (`agentcore create`, `agentcore add memory`, `agentcore deploy`,
> `agentcore status`, `agentcore invoke`) used in current AWS docs, and the
> `bedrock-agentcore-starter-toolkit` (`agentcore configure --entrypoint`, `agentcore launch`).
> **The agent code in this track is identical either way.** Use whichever the pre-flight installed,
> and follow its `--help`. Commands below follow the current AWS-documented flow.

---

## Step 0 — Run locally first

```bash
cd session-2-advanced/track-1-agentcore-runtime
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
python agent.py            # starts the AgentCore-compatible server on :8080
```

In another terminal:

```bash
agentcore invoke --dev '{"prompt": "Where is order #35476?"}'
# or: curl -s localhost:8080/invocations -d '{"prompt":"Where is order #35476?"}'
```

You should see the agent call the `get_order_status` tool and answer. Local success means the
runtime contract (`/invocations`, `/ping` on :8080) is satisfied.

## Step 1 — Deploy to AgentCore Runtime

```bash
# Package + deploy (builds an ARM64 container via CodeBuild, pushes to ECR, creates the runtime)
agentcore configure --entrypoint agent.py    # (starter-toolkit flow); or `agentcore create` project flow
agentcore launch                              # or `agentcore deploy`
agentcore status
```

Then invoke the deployed agent:

```bash
agentcore invoke '{"prompt": "Where is order #35476?"}'
```

Behind the scenes this calls `InvokeAgentRuntime`. Runtime gives you fast cold starts, autoscaling,
and **true session isolation** with no servers to manage.

## Step 2 — Sessions (isolation + continuity)

Pass a session ID so turns share context within a conversation but stay isolated across users:

```bash
agentcore invoke --session-id alice-001 '{"prompt": "My name is Alice and my order is #35476"}'
agentcore invoke --session-id alice-001 '{"prompt": "What is my order number?"}'
agentcore invoke --session-id bob-002   '{"prompt": "What is my order number?"}'   # must NOT know Alice's
```

In `agent.py`, the entrypoint reads `context.session_id` and `context.user_id` and scopes memory to
them. Each session runs isolated in the runtime.

## Step 3 — Add AgentCore Memory (NO_MEMORY -> STM -> LTM)

Deploy worked **without** memory (clean first deploy). Now add it:

```bash
# Create a managed memory resource with a semantic long-term strategy
agentcore add memory --name SupportMemory --strategies SEMANTIC
agentcore deploy
agentcore status         # confirm the memory is ACTIVE (extraction takes a few minutes)
```

AgentCore injects an env var `MEMORY_SUPPORTMEMORY_ID` into the runtime. Point the agent at it:

```bash
# Map the injected ID to the variable memory.py reads, then redeploy
export AGENTCORE_MEMORY_ID="$MEMORY_SUPPORTMEMORY_ID"
agentcore deploy
```

Now `memory.py` activates:
- **Short-term**: every turn is written via `session.add_turns(...)`.
- **Long-term**: the SEMANTIC strategy extracts facts/preferences; `load_context()` pulls the most
  relevant ones into the next prompt via `search_long_term_memories(...)`.

Test cross-session recall:

```bash
agentcore invoke --session-id alice-001 '{"prompt": "I prefer email updates, not SMS."}'
# ... later, a brand new session for the same user ...
agentcore invoke --session-id alice-009 '{"prompt": "How will you contact me about my order?"}'
# Should recall the email preference from long-term memory.
```

> Memory rollout is deliberately staged (deploy first, then enable) so a memory misconfig never
> blocks a working deploy. This mirrors AWS guidance.

## Step 4 — Observability

```bash
# Enable observability for the runtime (CloudWatch GenAI Observability / OTEL)
agentcore observability enable        # confirm exact subcommand via `agentcore --help`
```

Invoke a few times, then open **CloudWatch -> GenAI Observability** in `us-east-1`. You can inspect:
- the agent's execution path (model calls, tool calls) as spans,
- token usage and latency per step,
- failures and bottlenecks.

AgentCore emits standard **OpenTelemetry**, so the same traces can flow to any OTEL backend.

## Step 5 — Teardown (important on customer accounts)

```bash
agentcore destroy --dry-run     # preview
agentcore destroy               # remove runtime, ECR image, endpoint
agentcore remove memory --name SupportMemory && agentcore deploy
```

See [`bootstrap/`](../../bootstrap/) for the full teardown checklist.

---

## How this maps to the customer ask

> "Deploy a LangGraph agent to Bedrock with observability / memory / sessions."

- **LangGraph agent** -> `agent.py` (unchanged logic, wrapped for Runtime)
- **Sessions** -> `context.session_id` + Runtime session isolation (Step 2)
- **Memory** -> AgentCore Memory STM + LTM (Step 3)
- **Observability** -> CloudWatch GenAI Observability / OTEL (Step 4)

## Residency

All inference uses `us.amazon.nova-pro-v1:0` (US CRIS) from `us-east-1`, so
prompts/outputs stay within US Regions. Memory and observability data are created in `us-east-1`.
Track 4 covers the full residency story and the data-perimeter controls.

**Status:** authored. Validate the exact AgentCore CLI subcommands against the installed version
during the pre-flight; the agent/memory code is CLI-independent.
