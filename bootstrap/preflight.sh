#!/usr/bin/env bash
# Pre-flight check for the LangGraph + AgentCore workshop (us-east-1).
# Run in each participant's customer account before the session.
set -euo pipefail

REGION="${AWS_REGION:-us-east-1}"
echo "=============================================="
echo " Workshop pre-flight  (region: ${REGION})"
echo "=============================================="

echo
echo "-- Caller identity --"
aws sts get-caller-identity --query 'Arn' --output text || {
  echo "FAIL: AWS credentials not configured."; exit 1;
}

echo
echo "-- Local tooling --"
python3 --version || echo "WARN: python3 missing (need 3.10+)"
uv --version 2>/dev/null || echo "WARN: uv missing (https://docs.astral.sh/uv/)"
docker --version 2>/dev/null || echo "WARN: docker missing (needed for 'agentcore launch')"
agentcore --version 2>/dev/null || echo "WARN: agentcore CLI missing (pip install bedrock-agentcore-starter-toolkit OR npm i -g @aws/agentcore)"

echo
echo "-- US Amazon Nova inference profiles visible from ${REGION} --"
aws bedrock list-inference-profiles \
  --type-equals SYSTEM_DEFINED \
  --region "${REGION}" \
  --query "inferenceProfileSummaries[?starts_with(inferenceProfileId, 'us.amazon.nova')].inferenceProfileId" \
  --output table 2>/dev/null \
  || echo "WARN: could not list inference profiles (check bedrock permissions/region)."

echo
echo "-- Optional: test a Nova invocation via the US profile --"
echo "   aws bedrock-runtime converse \\"
echo "     --region ${REGION} \\"
echo "     --model-id us.amazon.nova-pro-v1:0 \\"
echo "     --messages '[{\"role\":\"user\",\"content\":[{\"text\":\"ping\"}]}]'"

echo
echo "NOTE: Bedrock model ACCESS must be enabled in the console for the Amazon Nova models"
echo "      in ALL US CRIS destination Regions, not only ${REGION}. Listing a profile"
echo "      does not guarantee access is granted for your account."
echo
echo "Pre-flight complete. Resolve any WARN/FAIL above before the session."
