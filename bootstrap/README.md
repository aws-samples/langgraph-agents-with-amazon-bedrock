# Bootstrap — Customer Account Setup, Pre-flight, Cost & Teardown

This workshop runs on **customer-owned AWS accounts** (not AWS-provisioned Workshop Studio
accounts), so each participant's account must be prepared in advance. ~15 participants, region
**us-east-1 (N. Virginia)**.

## Files

| File | Purpose |
|---|---|
| `preflight.sh` | Pre-session checks: identity, tooling, US Amazon Nova profiles |
| `iam-participant-policy.json` | Workshop-scoped IAM permissions (standalone policy doc) |
| `cfn-participant-setup.yaml` | CloudFormation that creates the policy and (optionally) attaches it |

## Pre-flight checklist (BEFORE the workshop)

- [ ] Region is **us-east-1** for all work
- [ ] Amazon Bedrock **model access** enabled in `us-east-1` **and all US CRIS destination Regions** for:
  - [ ] `amazon.nova-lite-v1:0`
  - [ ] `amazon.nova-pro-v1:0`
- [ ] IAM permissions applied (CloudFormation or policy below)
- [ ] `python >= 3.10`, `uv`, and **Docker** installed (Docker needed for `agentcore launch`)
- [ ] AgentCore CLI installed (`pip install bedrock-agentcore-starter-toolkit` or `npm i -g @aws/agentcore`)
- [ ] `bash preflight.sh` passes (no FAIL)

Run the checker:

```bash
cd bootstrap
AWS_REGION=us-east-1 bash preflight.sh
```

## Apply permissions

**Option A — CloudFormation (recommended for 15 accounts):**

```bash
aws cloudformation deploy \
  --region us-east-1 \
  --stack-name workshop-bootstrap \
  --capabilities CAPABILITY_NAMED_IAM \
  --template-file cfn-participant-setup.yaml \
  --parameter-overrides AttachToRoleName=<participant-role-name>
```

**Option B — attach the standalone policy** `iam-participant-policy.json` to the participant's
role/user via the console or `aws iam create-policy` + `attach-role-policy`.

> **Scope note:** this policy is **workshop-scoped and intentionally broad** for teaching (e.g.
> `bedrock-agentcore:*`). For production, scope actions/resources down. Bedrock model invocation is
> already restricted to **US regions** and to use **only via `us.` inference profiles** (see the
> `BedrockFoundationModelsEuViaEuProfileOnly` statement) — that part doubles as a Track 4 talking point.

## Multi-participant notes

- Use **per-participant resource name prefixes** (e.g. `workshop-<alias>-`) so Gateways, runtimes,
  ECR repos, and roles don't collide if accounts are shared.
- The IAM policy scopes role creation/PassRole to `workshop-*` / `AgentCore*` names — keep created
  roles within those prefixes.

## Cost awareness

- This workshop deliberately uses **managed AgentCore Memory** (not self-run OpenSearch Serverless),
  avoiding the biggest recurring cost.
- Main line items: AgentCore Runtime compute (per-second, only while active), ECR storage, CodeBuild
  minutes, Bedrock tokens, Gateway, Lambda, Secrets Manager. All modest for a workshop — **but must
  be torn down**.

## Teardown (AFTER the workshop)

- [ ] `agentcore destroy --dry-run` then `agentcore destroy` for each deployed runtime
- [ ] `agentcore gateway delete-mcp-gateway --name <name> --force` (Track 3)
- [ ] `agentcore remove memory --name <name>` then `agentcore deploy` (Track 1)
- [ ] `aws bedrock delete-guardrail --guardrail-identifier <id>` (Track 2)
- [ ] Delete the Track 3 Lambda, its VPC config, and Secrets Manager secrets (`internal/*`, `workshop/*`)
- [ ] Delete ECR repositories and CloudWatch log groups if not needed
- [ ] `aws cloudformation delete-stack --stack-name workshop-bootstrap --region us-east-1`
- [ ] Confirm no AgentCore sessions remain (`agentcore status`)

## Per-track resource summary (what gets created)

| Track | Creates | Teardown |
|---|---|---|
| 1 | AgentCore Runtime, Memory, ECR image, log group | `agentcore destroy`, `remove memory` |
| 2 | Bedrock Guardrail | `delete-guardrail` |
| 3 | Gateway, Cognito pool, Lambda, secret, (VPC bits) | `delete-mcp-gateway`, delete Lambda/secret |
| 4 | (none persistent) optional SCP at org level | remove SCP if applied |

**Status:** authored. Validate the US CRIS destination-Region list and confirm Bedrock model access
per account during the pre-flight.
