"""Server-side, read-only credit quotes for ElevenLabs Multilingual v2.

Proposed price: 3 Channel Coach credits per 1,000 characters, rounded up.
This is NOT an authorization to charge users or generate commercial audio.
The ElevenLabs Free plan must not be used for commercial generation.
"""
import math

MODEL_ID = "eleven_multilingual_v2"
CREDITS_PER_1000_CHARACTERS = 3
MAX_SECTION_CHARACTERS = 5000


def quote_voiceover_credits(text, model_id=MODEL_ID):
    """Return a deterministic quote; never spend credits or call a provider."""
    if model_id != MODEL_ID:
        raise ValueError("Unsupported voiceover model.")
    if not isinstance(text, str):
        raise ValueError("Section text must be a string.")
    characters = len(text.strip())
    if not 1 <= characters <= MAX_SECTION_CHARACTERS:
        raise ValueError("A section must contain between 1 and 5,000 characters.")
    credits = math.ceil(characters * CREDITS_PER_1000_CHARACTERS / 1000)
    return {
        "characters": characters,
        "credits": credits,
        "model_id": model_id,
        "rate_per_1000_characters": CREDITS_PER_1000_CHARACTERS,
    }
