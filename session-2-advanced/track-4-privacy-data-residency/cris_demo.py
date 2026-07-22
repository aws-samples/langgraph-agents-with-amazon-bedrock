"""Track 4 - Demonstrate US data-residency control via Bedrock inference profiles.

Run from us-east-1. Lists the US (`us.`) system-defined inference profiles visible from this
Region and invokes one, illustrating that a geographic US profile keeps inference within the US
geography (vs. a `global.` profile, which may route to any commercial Region).

Note: this workshop runs in US Regions (the Workshop Studio delivery environment). The mechanism
is identical for any geography - for an EU-resident deployment, set AWS_REGION to an EU Region
(e.g. eu-west-1) and use the `eu.` profile prefix (e.g. eu.amazon.nova-pro-v1:0).
"""

import os

import boto3

REGION = os.getenv("AWS_REGION", "us-east-1")
US_PROFILE = os.getenv("US_MODEL_ID", "us.amazon.nova-pro-v1:0")


def list_us_profiles():
    """Return the US geographic inference profile IDs visible from this Region."""
    client = boto3.client("bedrock", region_name=REGION)
    summaries = client.list_inference_profiles(typeEquals="SYSTEM_DEFINED").get(
        "inferenceProfileSummaries", []
    )
    return [
        s["inferenceProfileId"]
        for s in summaries
        if s.get("inferenceProfileId", "").startswith("us.")
    ]


def converse(model_id, prompt):
    client = boto3.client("bedrock-runtime", region_name=REGION)
    resp = client.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
    )
    return resp["output"]["message"]["content"][0]["text"]


if __name__ == "__main__":
    print(f"Source Region: {REGION}")
    print("US geographic inference profiles visible here:")
    for pid in list_us_profiles():
        print(f"  - {pid}")
    print(f"\nInvoking US profile {US_PROFILE} (inference stays within US Regions)...")
    print(converse(US_PROFILE, "In one sentence, what is data residency?"))
