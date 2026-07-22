# Session 1 — Foundations: Building Agentic Systems with LangGraph

**Audience:** Software Engineers new to building applications with LLMs.
**Focus:** Building **agentic systems** — reasoning + tool use + control flow. This session is
explicitly **not** about RAG; there is no vector store or knowledge-base retrieval here.

Session 1 is delivered using the foundation labs in **this repo**:
**[`Lab_1`](../Lab_1/) … [`Lab_6`](../Lab_6/)**. This folder holds the framing and the
US retargeting guide; the labs themselves are not duplicated.

## Learning objectives

By the end of Session 1, participants can:

1. Explain the agent loop (reason -> act -> observe) and when an agent beats a single prompt.
2. Build agents with LangGraph primitives: **nodes, edges, conditional routing, and state**.
3. Give agents **tools** (functions / external APIs) and let the model decide when to call them.
4. Add **persistence, sessions, and streaming** for long-running interactions.
5. Insert **human-in-the-loop** checkpoints (approve / edit state / resume).
6. Compose a **multi-agent** system for a multi-step task.

## Module map (the labs in this repo)

Retargeting = run in `us-east-1`, use the US CRIS model IDs, and frame everything as *agentic
systems* (drop any retrieval/RAG emphasis). Apply it with [`RETARGETING.md`](./RETARGETING.md).

| Module | Lab | Theme |
|---|---|---|
| 1. Agent from scratch | [`Lab_1`](../Lab_1/) | ReAct loop, tool use, the bare mechanics |
| 2. LangGraph components | [`Lab_2`](../Lab_2/) | Nodes, edges, state, conditional routing |
| 3. Tools & external APIs | [`Lab_3`](../Lab_3/) | Equipping agents with capabilities (tool use, not RAG) |
| 4. Persistence & streaming | [`Lab_4`](../Lab_4/) | Checkpointers, threads/sessions, streaming events |
| 5. Human-in-the-loop | [`Lab_5`](../Lab_5/) | Interrupts, approvals, state edits, resume |
| 6. Multi-agent capstone | [`Lab_6`](../Lab_6/) | A multi-step agentic system |

> Module 3 uses a web-search/API tool as a *capability* example; if a lab leans on retrieval
> framing, reword it to stay agent-centric.

## Setup

Follow the original environment setup in the repo [`README.md`](../README.md), then apply the
US changes in [`RETARGETING.md`](./RETARGETING.md).

## Output that carries into Session 2

The capstone agent from [`Lab_6`](../Lab_6/) (or a simplified single agent) is the artifact that
Session 2 deploys, hardens, and integrates. Keep it runnable as a plain Python entrypoint so
[Track 1](../session-2-advanced/track-1-agentcore-runtime/) can wrap it in an AgentCore
`@app.entrypoint` with no rewrite.

**Status:** framing complete. Retargeting edits are applied to the `Lab_*` notebooks at delivery.
