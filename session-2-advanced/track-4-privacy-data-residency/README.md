# Track 4 — Privacy, Data Security & Data Residency for Amazon Nova

Give the Security Engineers a defensible answer to: *"If we run Amazon Nova on Bedrock in us-east-1,
where does our data go, and how do we prove it stays in the US?"* Mostly theory + demo, grounded in
the labs already deployed in `us-east-1`.

> **Delivery note:** This workshop runs in **US Regions** (`us-east-1`) because the Workshop Studio
> environment is US-only. The data-residency *mechanism* is identical for any geography: for an
> **EU-resident** production deployment, switch the source Region to `eu-west-1` and use the `eu.`
> profile prefix (`eu.amazon.nova-pro-v1:0`). Everything else in this track applies unchanged.

## Objectives

1. Explain the **Amazon Nova inference data flow** on Bedrock and where data is (and isn't) stored.
2. Use **US geographic cross-region inference (CRIS)** to keep processing within the US.
3. Distinguish **in-Region** vs **geographic (US)** vs **global** inference and the tradeoffs.
4. Enforce a **data perimeter**: SCP region boundaries, VPC endpoints / PrivateLink.
5. Account for residency of **Memory, observability traces, and Guardrail logs** (Tracks 1–3).

## Files

| File | Purpose |
|---|---|
| `cris_demo.py` | Lists US (`us.`) inference profiles and invokes one from `us-east-1` |
| `scp-us-data-perimeter.json` | Sample SCP denying Bedrock outside US Regions |

## The three inference routing modes

| Mode | Model ID prefix | Routing | Use when |
|---|---|---|---|
| In-Region | `amazon.nova-…` | Single Region only | Strictest residency; lower throughput ceiling |
| **Geographic (US)** | `us.amazon.nova-…` | **Only US Regions** | **This workshop** — US residency + higher throughput |
| Global | `global.amazon.nova-…` | Any commercial Region worldwide | Max capacity / lowest cost; **not** for US residency |

This workshop uses **`us.amazon.nova-pro-v1:0`** from `us-east-1`.

## How US CRIS protects residency (verified)

- A US geographic profile routes inference **only to AWS Regions within the US**. A request from a
  US source Region is never routed outside the US.
- **Storage**: by default data is stored only in the **source Region**. Input prompts/outputs may
  *move between US Regions* during inference but aren't stored in destination Regions (except, for
  some models, abuse-detection retention).
- **In transit**: data stays on the **encrypted AWS backbone** — it does not traverse the public
  internet.
- Bedrock does **not** use your prompts or outputs to train models.

## Demo

```bash
cd session-2-advanced/track-4-privacy-data-residency
uv venv && source .venv/bin/activate
uv pip install boto3
python cris_demo.py
```

You'll see the US profiles available from `us-east-1` and a live invocation through the US profile.
Contrast with a `global.` profile to make the routing/residency difference concrete.

## Enforcing a data perimeter (defense in depth)

### 1. IAM scoping for Geo CRIS

Geo CRIS requires `bedrock:InvokeModel` on **both** the inference-profile ARN **and** the
foundation-model ARN in the source **and all US destination Regions**. Scope with the
`bedrock:InferenceProfileArn` condition. (The exact policy is in [`../../bootstrap/`](../../bootstrap/).)

### 2. SCP region boundary

Apply [`scp-us-data-perimeter.json`](./scp-us-data-perimeter.json) at the org/OU to **deny all
Bedrock calls outside US Regions**. Important: the allow-list must include **every US CRIS
destination Region** for the profile, or geo routing will fail. Validate the destination list for
your chosen profile before enforcing.

### 3. Private connectivity (VPC endpoints / PrivateLink)

Run agents in a VPC and reach Bedrock through **interface VPC endpoints (PrivateLink)** so
agent-to-Bedrock traffic never leaves the AWS network. Combine with the Track 3 private path
(VPC Lattice / VPC-attached Lambda) so the internal GraphQL path is private too.

## Residency of the *rest* of the system (tie-back to Tracks 1–3)

Data residency isn't just the model call. Account for:

- **AgentCore Memory** (Track 1): created in `us-east-1`; STM/LTM records live there.
- **Observability traces** (Track 1): CloudWatch GenAI Observability in `us-east-1`.
- **Guardrail + model-invocation logs** (Track 2): logs keep the *original* (unmasked) input — keep
  them in-Region and apply **CloudWatch Logs data protection** to mask sensitive fields at rest.
- **Gateway / Secrets / GraphQL** (Track 3): keep Gateway, Lambda, Secrets Manager, and EC2 in
  `us-east-1`.

The residency story is only as strong as its weakest component — enumerate all of them.

## What to tell auditors (summary)

- Model: US geographic inference profile; inference confined to US Regions; encrypted on the AWS
  backbone; no training on customer data.
- Controls: SCP region boundary + least-privilege IAM (scoped to the US profile) + PrivateLink.
- Supporting data (memory, logs, traces, secrets): all provisioned in `us-east-1`.

## How this maps to the customer ask

> "Privacy & Data Security, data residency for Amazon Nova."

- **Data residency for Amazon Nova** -> US CRIS (`cris_demo.py`, the routing table)
- **Privacy & data security** -> SCP perimeter, PrivateLink, log data protection, no-training posture
- Cross-references the residency of Memory/Observability/Guardrail logs/Gateway from Tracks 1–3

**Status:** authored. Validate the US CRIS destination-Region list for the chosen profile (for the
SCP allow-list) against current docs during the pre-flight.
