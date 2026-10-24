"""Generate private-download plans from server-verified job records only.

The actual API handler must authenticate the session, query a job scoped to
that user, and generate a short-lived URL with a private storage client.
This module performs no network calls and never accepts a client-supplied path.
"""
from voiceover_private_download import validate_private_clip_request
from voiceover_storage_paths import BUCKET

MAX_SIGNED_URL_SECONDS = 60


def plan_private_clip_download(verified_user_id, verified_job, ttl_seconds=60):
    if type(ttl_seconds) is not int or not 1 <= ttl_seconds <= MAX_SIGNED_URL_SECONDS:
        raise ValueError("Invalid download link lifetime.")
    path = validate_private_clip_request(verified_user_id, verified_job)
    return {
        "bucket": BUCKET,
        "object_path": path,
        "expires_in": ttl_seconds,
        "download_filename": "voiceover.mp3",
    }
