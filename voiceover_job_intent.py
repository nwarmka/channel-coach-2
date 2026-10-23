"""Deterministic metadata for future idempotent voiceover jobs.

These helpers never insert database rows, spend credits, or call ElevenLabs.
The request UUID must be minted by a trusted backend and persisted for retries.
"""
import uuid

from voiceover_quote import create_quote_snapshot


def build_job_intent(user_id, request_key, section_id, text, voice_id):
    try:
        user = str(uuid.UUID(str(user_id)))
        key = str(uuid.UUID(str(request_key)))
    except (TypeError, ValueError, AttributeError) as exc:
        raise ValueError("Valid user and request UUIDs are required.") from exc
    snapshot = create_quote_snapshot(str(section_id), text, voice_id)
    return {
        "user_id": user,
        "request_key": key,
        "section_sha256": snapshot["text_sha256"],
        "voice_id": snapshot["voice_id"],
        "model_id": snapshot["model_id"],
        "characters": len(text.strip()),
        "quoted_credits": snapshot["credits"],
    }


def intent_matches_existing(intent, existing):
    """Reject reuse of an idempotency key for a different request."""
    if not isinstance(existing, dict):
        return False
    fields = ("user_id", "request_key", "section_sha256", "voice_id",
              "model_id", "characters", "quoted_credits")
    return all(intent.get(field) == existing.get(field) for field in fields)
