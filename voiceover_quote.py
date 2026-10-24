"""Immutable voiceover quote fingerprints and stale-quote checks.

This module is deliberately read-only. A matching quote is NOT authentication,
permission to spend credits, or authorization to generate audio.
"""
import hashlib

from voiceover_pricing import quote_voiceover_credits


def create_quote_snapshot(section_id, text, voice_id):
    if not isinstance(section_id, str) or not section_id.isdecimal():
        raise ValueError("Select a valid section.")
    if not isinstance(voice_id, str) or not voice_id.strip() or len(voice_id) > 128:
        raise ValueError("Select a valid narrator voice.")
    quote = quote_voiceover_credits(text)
    return {
        "section_id": section_id,
        "voice_id": voice_id,
        "text_sha256": hashlib.sha256(text.strip().encode("utf-8")).hexdigest(),
        "credits": quote["credits"],
        "model_id": quote["model_id"],
    }


def quote_is_current(snapshot, section_id, text, voice_id):
    if not isinstance(snapshot, dict):
        return False
    try:
        expected = create_quote_snapshot(str(section_id), text, voice_id)
    except (ValueError, TypeError, AttributeError):
        return False
    return snapshot == expected
