"""Private voiceover clip download validation.

Read-only: this module does not connect to storage or generate signed URLs.
Only server-verified job records may be passed to this helper.
"""
import uuid
from voiceover_storage_paths import voiceover_object_path


def validate_private_clip_request(user_id, job):
    """Return a canonical private storage key after strict ownership checks."""
    try:
        user = str(uuid.UUID(str(user_id)))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError("Sign in to access voiceover clips.") from exc
    if not isinstance(job, dict):
        raise ValueError("A verified voiceover job is required.")
    try:
        owner = str(uuid.UUID(str(job.get("user_id"))))
        job_id = str(uuid.UUID(str(job.get("id"))))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError("Invalid voiceover job.") from exc
    if owner != user:
        raise PermissionError("This voiceover clip belongs to another account.")
    if job.get("status") != "completed":
        raise ValueError("The voiceover clip is not ready.")
    expected = voiceover_object_path(user, job_id)
    if job.get("storage_path") != expected:
        raise ValueError("The private clip path is invalid.")
    return expected
