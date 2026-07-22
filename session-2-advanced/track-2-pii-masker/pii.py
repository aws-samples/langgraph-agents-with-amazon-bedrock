"""PII detection & masking helpers.

Two independent controls, used together for defense in depth:
  - comprehend_mask(): deterministic, app-layer masking via Amazon Comprehend.
  - guardrail_apply(): managed, model-layer masking via a Bedrock Guardrail
    (the ApplyGuardrail API works on arbitrary text, model-independent).
"""

import os

import boto3

REGION = os.getenv("AWS_REGION", "us-east-1")

_comprehend = None
_bedrock_runtime = None


def _comp():
    global _comprehend
    if _comprehend is None:
        _comprehend = boto3.client("comprehend", region_name=REGION)
    return _comprehend


def comprehend_mask(text, language_code="en", min_score=0.5):
    """Mask PII spans detected by Amazon Comprehend.

    Each detected entity is replaced with ``[TYPE]`` (e.g. ``[NAME]``).
    Returns ``(masked_text, entities)``.
    """
    if not text:
        return text, []
    resp = _comp().detect_pii_entities(Text=text, LanguageCode=language_code)
    entities = [e for e in resp.get("Entities", []) if e.get("Score", 0) >= min_score]
    masked = text
    # Replace right-to-left so earlier offsets stay valid.
    for e in sorted(entities, key=lambda x: x["BeginOffset"], reverse=True):
        masked = masked[: e["BeginOffset"]] + f"[{e['Type']}]" + masked[e["EndOffset"]:]
    return masked, entities


def _brt():
    global _bedrock_runtime
    if _bedrock_runtime is None:
        _bedrock_runtime = boto3.client("bedrock-runtime", region_name=REGION)
    return _bedrock_runtime


def guardrail_apply(text, guardrail_id, guardrail_version="DRAFT", source="INPUT"):
    """Apply a Bedrock Guardrail to arbitrary text (model-independent).

    ``source`` is ``"INPUT"`` or ``"OUTPUT"``. Returns
    ``(possibly_masked_text, intervened)`` where ``intervened`` is True when the
    guardrail took action (masked or blocked).
    """
    if not (text and guardrail_id):
        return text, False
    resp = _brt().apply_guardrail(
        guardrailIdentifier=guardrail_id,
        guardrailVersion=guardrail_version,
        source=source,
        content=[{"text": {"text": text}}],
    )
    intervened = resp.get("action") == "GUARDRAIL_INTERVENED"
    outputs = resp.get("outputs") or []
    masked = outputs[0]["text"] if (intervened and outputs) else text
    return masked, intervened
