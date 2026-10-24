"""Pure, offline MP3 ZIP packaging for future authenticated downloads.

This does not retrieve clips from storage, verify ownership, or expose a
download endpoint. The caller must do those checks before supplying bytes.
"""
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED

from voiceover_clip_manifest import build_clip_manifest

MAX_CLIP_BYTES = 25 * 1024 * 1024
MAX_BUNDLE_BYTES = 100 * 1024 * 1024


def package_voiceover_mp3s(clips):
    """Return ZIP bytes for completed clips, preserving caller-supplied order.

    Each item needs id, status='completed', and audio_bytes. All checks happen
    before creating the archive. Never trust client-supplied clip bytes in an
    authenticated endpoint; load them from verified private storage instead.
    """
    manifest = build_clip_manifest(clips)
    total = 0
    for clip in clips:
        data = clip.get("audio_bytes")
        if not isinstance(data, bytes) or not data.startswith(b"ID3") and not (
            len(data) >= 2 and data[0] == 0xFF and data[1] & 0xE0 == 0xE0
        ):
            raise ValueError("Clip is not recognizable MP3 audio.")
        if not 0 < len(data) <= MAX_CLIP_BYTES:
            raise ValueError("An MP3 clip exceeds the allowed size.")
        total += len(data)
        if total > MAX_BUNDLE_BYTES:
            raise ValueError("The ZIP bundle exceeds the allowed size.")

    stream = BytesIO()
    with ZipFile(stream, "w", compression=ZIP_DEFLATED, compresslevel=6) as archive:
        for entry, clip in zip(manifest, clips):
            archive.writestr(entry["filename"], clip["audio_bytes"])
    return stream.getvalue()
