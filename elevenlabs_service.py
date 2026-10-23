"""Server-side ElevenLabs text-to-speech adapter for Channel Coach.

This module is intentionally not exposed as a public endpoint or wired to the
credit ledger yet. UI integration must authenticate users, enforce quotas,
and calculate/approve credit costs before calling generate_speech().
"""
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

import requests

API_BASE = "https://api.elevenlabs.io/v1"
DEFAULT_MODEL = "eleven_multilingual_v2"
MAX_SECTION_CHARS = 5000


class ElevenLabsError(RuntimeError):
    """A safe-to-display ElevenLabs integration error."""


def _headers():
    key = os.getenv("ELEVENLABS_API_KEY", "").strip()
    if not key:
        raise ElevenLabsError("ElevenLabs is not configured on the server.")
    return {"xi-api-key": key}


def list_voices():
    """Return available voice IDs and names for a server-side voice picker."""
    try:
        response = requests.get(
            f"{API_BASE}/voices",
            headers=_headers(),
            timeout=20,
        )
        response.raise_for_status()
        return [
            {"voice_id": voice["voice_id"], "name": voice.get("name", "Unnamed")}
            for voice in response.json().get("voices", [])
            if voice.get("voice_id")
        ]
    except requests.RequestException as exc:
        raise ElevenLabsError("Could not load ElevenLabs voices.") from exc


def generate_speech(text, voice_id, model_id=DEFAULT_MODEL):
    """Generate one section as an MP3; return its temporary server-side path.

    Callers are responsible for authenticating the user, checking quotas and
    charging credits. Do not expose this function through an unauthenticated API.
    """
    text = (text or "").strip()
    if not text or len(text) > MAX_SECTION_CHARS:
        raise ValueError(f"Section must contain 1–{MAX_SECTION_CHARS} characters.")
    if not voice_id or not isinstance(voice_id, str):
        raise ValueError("Select a valid voice.")
    if model_id != DEFAULT_MODEL:
        raise ValueError("Unsupported voiceover model.")

    try:
        response = requests.post(
            f"{API_BASE}/text-to-speech/{voice_id}",
            headers={**_headers(), "Content-Type": "application/json", "Accept": "audio/mpeg"},
            json={"text": text, "model_id": model_id},
            timeout=120,
            stream=True,
        )
        response.raise_for_status()
        with NamedTemporaryFile(prefix="cc_voice_", suffix=".mp3", delete=False) as out:
            try:
                for chunk in response.iter_content(chunk_size=65536):
                    if chunk:
                        out.write(chunk)
            except Exception:
                Path(out.name).unlink(missing_ok=True)
                raise
            return out.name
    except requests.RequestException as exc:
        raise ElevenLabsError(
            "Voiceover generation failed. Please check the ElevenLabs account and try again."
        ) from exc
