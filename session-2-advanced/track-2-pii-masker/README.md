# Track 2 — PII Masker: Detection, Guardrails & Masking in Agent Requests

Protect personal data flowing through the agent using **two independent controls** — one at the
application boundary, one at the model boundary — so a gap in either is caught by the other.

## Objectives

1. Detect PII deterministically with **Amazon Comprehend** (`DetectPiiEntities`).
2. Configure an **Amazon Bedrock Guardrail** with a sensitive-information policy (anonymize / block).
3. Apply masking on the way **in** (before the model) and on the way **out** (before the user).
4. Reason about **masking vs. utility** and where raw data can still leak (logs, tool params).

## Files

| File | Purpose |
|---|---|
| `pii.py` | `comprehend_mask()` (app-layer) and `guardrail_apply()` (model-layer, `ApplyGuardrail`) |
| `guardrail.py` | One-time creation of a Bedrock Guardrail with a PII policy |
| `agent_pii.py` | LangGraph pipeline: `mask_input -> call_agent -> scrub_output` (AgentCore-deployable) |

## The two layers (defense in depth)

```
user prompt
   │  [App layer]  Comprehend masks NAME/EMAIL/PHONE/... -> [TYPE]
   ▼
LangGraph agent   <-- [Model layer] Bedrock Guardrail anonymizes/blocks PII on input & output
   ▼
guardrail + Comprehend scrub the answer
   ▼
safe answer to user
```

- **App layer (Comprehend):** deterministic, auditable, runs before any model sees the text. Good
  for known formats and for masking *before* data ever leaves your code path.
- **Model layer (Guardrails):** managed, ML-based, model-independent (the `ApplyGuardrail` API also
  protects non-Bedrock or self-hosted models). Masks to `{NAME}`, `{EMAIL}`, etc., or blocks.

## Setup

```bash
cd session-2-advanced/track-2-pii-masker
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

# 1) Create the guardrail (once) and capture its id/version
python guardrail.py
export GUARDRAIL_ID=<printed-id>
export GUARDRAIL_VERSION=<printed-version>

# 2) Run the agent locally
python agent_pii.py
# in another terminal:
agentcore invoke --dev '{"prompt": "Hi, I am Jane Doe (jane@acme.com). Where is order #35476?"}'
```

Expected: the model receives `Hi, I am [NAME] ([EMAIL]). Where is order #35476?` — it can still
look up the order, but never sees the real name/email. The order id is intentionally **not** masked
(the tool needs it — see below).

## Masking vs. utility (key teaching point)

Masking reduces what the model and tools can use. If you anonymize a value a tool needs (e.g. an
order id), the tool can't act on it. Strategies:

- **Mask only what isn't needed downstream** (default here: names/emails/phones, not order ids).
- **Reversible tokenization**: replace PII with a token, keep a secure map, de-tokenize after — vs.
  irreversible redaction. Choose per data type and regulatory need.
- Try it: uncomment the `EmployeeId` regex in `guardrail.py` and watch a needed value disappear.

## Security notes (for the Security Engineers)

- **Logs keep the original**: Bedrock model-invocation logs record the *unmodified* input even when
  a guardrail masks it. Protect logs separately with **CloudWatch Logs data protection**.
- **Tool-call params aren't covered**: the PII filter applies to text input/responses, not to
  `tool_use` function-call parameters — mask those yourself (the app layer here helps).
- **Block vs. anonymize**: secrets, card numbers, SSN/PIN are set to **BLOCK**; identity fields are
  **ANONYMIZE** so the conversation still works.
- Guardrails are **model-independent** via `ApplyGuardrail`, so the same policy protects any model.

## Residency

Comprehend and Guardrails run in `us-east-1`; model calls use the US CRIS profile. No PII leaves the
US. See Track 4.

## Teardown

```bash
aws bedrock delete-guardrail --guardrail-identifier "$GUARDRAIL_ID" --region us-east-1
```

## How this maps to the customer ask

> "PII Masker: PII detection, Guardrails, PII masking with agent requests."

- **PII detection** -> Amazon Comprehend (`pii.py`)
- **Guardrails** -> Bedrock Guardrail sensitive-information policy (`guardrail.py`)
- **Masking in agent requests** -> LangGraph `mask_input` / `scrub_output` nodes (`agent_pii.py`)

**Status:** authored. Confirm the `langchain-aws` guardrail parameter name and the Guardrails PII
entity list against current versions during the pre-flight.
