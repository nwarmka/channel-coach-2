"""Safe signed URL creation for authenticated private voiceover clips.

The supplied Supabase client must be authenticated and have storage permissions.
The caller must derive verified_user_id from a server-verified session, never
from a client-supplied user ID. Only a completed, owned DB job is eligible.
"""
from voiceover_download_plan import plan_private_clip_download
from voiceover_owned_job_lookup import get_owned_completed_voiceover_job


def create_private_clip_download_url(authenticated_client, verified_user_id, job_id):
    job = get_owned_completed_voiceover_job(
        authenticated_client, verified_user_id, job_id
    )
    plan = plan_private_clip_download(verified_user_id, job)
    result = (
        authenticated_client.storage
        .from_(plan["bucket"])
        .create_signed_url(plan["object_path"], plan["expires_in"])
    )
    if not isinstance(result, dict):
        raise RuntimeError("Could not create a private download link.")
    url = result.get("signedURL") or result.get("signedUrl")
    if not isinstance(url, str) or not url.startswith("https://"):
        raise RuntimeError("Could not create a secure download link.")
    return {"url": url, "expires_in": plan["expires_in"]}
