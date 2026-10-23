"""Authenticated job lookup for future private voiceover downloads.

Callers must provide a Supabase client bound to a server-verified session.
Both explicit user scoping and RLS are required. Never accepts a storage key
or a URL from the browser.
"""
import uuid


def get_owned_completed_voiceover_job(authenticated_client, verified_user_id, job_id):
    if authenticated_client is None:
        raise ValueError("An authenticated Supabase client is required.")
    try:
        user = str(uuid.UUID(str(verified_user_id)))
        job = str(uuid.UUID(str(job_id)))
    except (TypeError, ValueError, AttributeError) as exc:
        raise ValueError("Valid user and job IDs are required.") from exc
    result = (
        authenticated_client.table("voiceover_generation_jobs")
        .select("id,user_id,status,storage_path")
        .eq("id", job)
        .eq("user_id", user)
        .eq("status", "completed")
        .limit(1)
        .execute()
    )
    rows = result.data or []
    if len(rows) != 1:
        raise FileNotFoundError("Voiceover clip not found.")
    record = rows[0]
    from voiceover_private_download import validate_private_clip_request
    validate_private_clip_request(user, record)
    return record
