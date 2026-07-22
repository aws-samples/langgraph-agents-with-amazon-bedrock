# Session 1 — Retargeting Guide (US / us-east-1)

Session 1 uses the foundation labs in this repo (**[`../Lab_1`](../Lab_1/) … [`../Lab_6`](../Lab_6/)**).
Apply the small changes below to those labs. Nothing here changes lab *logic* — only region, model
IDs, and framing.

## Change 1 — Region: use `us-east-1`

- In the repo's `.env` (copied from [`../env.tmp`](../env.tmp)), set the region to **`us-east-1`**.
- Rationale: all inference must originate in the US for residency (see Session 2 / Track 4).

## Change 2 — Model IDs: US Amazon Nova (already applied)

The labs now ship with the **US** (`us.`) Amazon Nova inference profiles, so **no model-ID edit is
required**:

| Role | Model ID (US) |
|---|---|
| Fast default | `us.amazon.nova-lite-v1:0` |
| Reasoning | `us.amazon.nova-pro-v1:0` |

Notes:
- Enable **model access for both Amazon Nova Lite and Nova Pro in `us-east-1` and all US CRIS
  destination Regions**, not only `us-east-1` (see [`../bootstrap/`](../bootstrap/)).
- Amazon Nova does **not** support the `top_k` inference parameter; the labs' inference configs
  use only `temperature`, `top_p`/`topP`, `max_tokens`/`maxTokens`, and `stop_sequences`/`stopSequences`.

## Change 3 — Framing: agentic systems, not RAG

This session is positioned as **building agentic systems**. Keep the language tool- and
control-flow-centric:

- **Lab 3 (search):** present the search tool as an agent **capability / tool use**, not as
  retrieval-augmented generation. Do not frame Tavily/DuckDuckGo as "RAG over a knowledge base."
- There is intentionally **no vector store / knowledge base** anywhere in Session 1.
- If asked about RAG, note it is out of scope by design for this audience and goal.

## Change 4 — Search tool key is optional

The labs support a **DuckDuckGo fallback** when no Tavily key is present
(`utils.get_search_tool()`), and Labs 2/4/5 have a one-line swap documented in the repo
[`README.md`](../README.md). For a foundations session, the keyless fallback is fine; a Tavily key
only sharpens Lab 3's structured-results comparison.

## Change 5 — Keep the capstone deployable

The artifact that flows into Session 2 is the **[`Lab_6`](../Lab_6/) capstone agent** (or a trimmed
single agent). Keep it runnable as a plain Python entrypoint (a function that takes a prompt and
returns a response) so Track 1 can wrap it in an AgentCore `@app.entrypoint` with no rewrite.

## Per-lab checklist

| Lab | Objective in this session | Retarget action |
|---|---|---|
| [Lab_1](../Lab_1/) | ReAct loop / tool mechanics | Region only (US Nova already set) |
| [Lab_2](../Lab_2/) | LangGraph nodes/edges/state/routing | Region only; keyless search swap optional |
| [Lab_3](../Lab_3/) | Tools & external APIs (capability) | Reframe away from RAG |
| [Lab_4](../Lab_4/) | Persistence, sessions, streaming | Region only; keyless search swap optional |
| [Lab_5](../Lab_5/) | Human-in-the-loop | Region only; keyless search swap optional |
| [Lab_6](../Lab_6/) | Multi-agent capstone | Keep entrypoint clean for Session 2 |

## Facilitator note

Apply these edits to the `Lab_*` notebooks in this repo (or distribute a patch / a short setup
script) during Session 1 setup. They are region/model/framing changes only — the lab logic is
unchanged.

**Status:** complete (guide). Edits are applied to the labs at delivery time.
