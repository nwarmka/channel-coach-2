"""Fail-closed server-side voiceover generation authorization.

No paid API calls are made by this module. The release gate stays off until
commercial ElevenLabs rights, durable idempotent jobs, authenticated sessions,
and credit/refund reconciliation have been reviewed and tested.
"""
import os

from voiceover_pricing import quote_voiceover_credits


class VoiceoverUnavailable(RuntimeError):
    """A generation request is blocked before any billing or provider call."""


def validate_generation_request(user_id, text, voice_id, approved_credits):
    """Validate inputs, then fail closed until commercial release is ready.

    This is intentionally not a charging or TTS function.
    """
    import uuid

    try:
        user_id = str(uuid.UUID(str(user_id)))
    except (TypeError, ValueError, AttributeError) as exc:
        raise ValueError("A verified signed-in user is required.") from exc
    if not isinstance(voice_id, str) or not voice_id.strip():
        raise ValueError("Select a narrator voice.")
    quote = quote_voiceover_credits(text)
    if type(approved_credits) is not int or approved_credits != quote["credits"]:
        raise ValueError("The approved quote does not match the current price.")
    if os.getenv("CHANNEL_COACH_VOICEOVER_GENERATION_ENABLED", "").lower() == "true":
        # An environment toggle alone must NEVER unlock an incomplete payment flow.
        raise VoiceoverUnavailable("Voiceover generation is not ready for release.")
    raise VoiceoverUnavailable("Voiceover generation is not yet available.")
