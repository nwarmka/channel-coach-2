"""Voiceover credit quotes.

Pricing is deliberately disabled until the owner sets and validates a rate.
Do not infer an ElevenLabs cost from characters alone: model, subscription,
and account terms can change.
"""
import math
import os


def quote_voiceover_credits(text, model_id="eleven_multilingual_v2"):
    """Return a quote for explicit approval, or None if pricing is unconfigured."""
    if model_id != "eleven_multilingual_v2":
        raise ValueError("Unsupported voiceover model.")
    characters = len((text or "").strip())
    if not 1 <= characters <= 5000:
        raise ValueError("A section must contain between 1 and 5,000 characters.")

    raw_rate = os.getenv("CHANNEL_COACH_VOICEOVER_CREDITS_PER_1000_CHARS", "")
    if not raw_rate:
        return None
    try:
        rate = float(raw_rate)
    except ValueError as exc:
        raise RuntimeError("Voiceover pricing configuration is invalid.") from exc
    if not math.isfinite(rate) or rate <= 0:
        raise RuntimeError("Voiceover pricing must be a positive finite number.")

    credits = math.ceil(characters * rate / 1000)
    return {"characters": characters, "credits": max(1, credits), "model_id": model_id}
