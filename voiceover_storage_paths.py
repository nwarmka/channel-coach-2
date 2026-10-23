"""Private object key validation for future per-user MP3 storage.

This module does not create a bucket or upload any data. Storage must remain
private, with server-verified ownership and short-lived signed download URLs.
"""
import uuid

BUCKET = "voiceover-clips"


def voiceover_object_path(user_id, job_id):
    """Generate a canonical key from server-verified UUIDs only."""
    try:
        user = str(uuid.UUID(str(user_id)))
        job = str(uuid.UUID(str(job_id)))
    except (TypeError, ValueError, AttributeError) as exc:
        raise ValueError("Valid user and job IDs are required.") from exc
    return f"{user}/{job}.mp3"


def is_owned_voiceover_path(user_id, job_id, path):
    """Compare exact canonical paths, not prefix matches or user input paths."""
    try:
        expected = voiceover_object_path(user_id, job_id)
    except ValueError:
        return False
    return isinstance(path, str) and path == expected
