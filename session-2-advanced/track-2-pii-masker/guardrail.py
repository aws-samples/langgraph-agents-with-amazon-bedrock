"""Create/manage a Bedrock Guardrail with a sensitive-information (PII) policy.

Run once to create the guardrail, then export the printed GUARDRAIL_ID /
GUARDRAIL_VERSION for the agent to use.

Actions: ANONYMIZE (mask, e.g. -> {NAME}) or BLOCK (reject the whole request/response).
"""

import os

import boto3

REGION = os.getenv("AWS_REGION", "us-east-1")

# Mask these (keep the conversation usable).
PII_ANONYMIZE = ["NAME", "EMAIL", "PHONE", "ADDRESS", "USERNAME", "AGE", "IP_ADDRESS"]
# Block outright (never appropriate to echo back).
PII_BLOCK = [
    "PASSWORD",
    "CREDIT_DEBIT_CARD_NUMBER",
    "US_SOCIAL_SECURITY_NUMBER",
    "AWS_SECRET_KEY",
    "PIN",
]


def create_pii_guardrail(name="workshop-pii-guardrail"):
    """Create the guardrail and publish a version. Returns (guardrail_id, version)."""
    bedrock = boto3.client("bedrock", region_name=REGION)
    pii_entities = [{"type": t, "action": "ANONYMIZE"} for t in PII_ANONYMIZE] + [
        {"type": t, "action": "BLOCK"} for t in PII_BLOCK
    ]
    resp = bedrock.create_guardrail(
        name=name,
        description="Workshop: anonymize common PII; block secrets/cards/SSN/PIN.",
        blockedInputMessaging="Your request was blocked for containing sensitive data.",
        blockedOutputsMessaging="The response was blocked for containing sensitive data.",
        sensitiveInformationPolicyConfig={
            "piiEntitiesConfig": pii_entities,
            # Custom regexes go here, e.g. internal employee IDs. Caution: do NOT
            # anonymize values your tools still need (see README: masking vs utility).
            # "regexesConfig": [
            #     {"name": "EmployeeId", "description": "EMP-12345",
            #      "pattern": r"EMP-\\d{5}", "action": "ANONYMIZE"}
            # ],
        },
    )
    guardrail_id = resp["guardrailId"]
    version = bedrock.create_guardrail_version(guardrailIdentifier=guardrail_id)["version"]
    return guardrail_id, version


if __name__ == "__main__":
    gid, ver = create_pii_guardrail()
    print(f"Created guardrail {gid} (version {ver}).")
    print("Export these for the agent:")
    print(f"  export GUARDRAIL_ID={gid}")
    print(f"  export GUARDRAIL_VERSION={ver}")
