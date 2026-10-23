"""Read-only voiceover job status helper.

Never uses a service-role key, creates jobs, or deducts credits.
A caller must supply a Supabase client with a *verified user session*.
"""
import uuid

ALLOWED_STATUSES = frozenset({
    "pending", "reserved", "processing", "completed", "failed", "review_required"
})


def list_voiceover_jobs(authenticated_client, verified_user_id, limit=25):
    """List only the verified user's jobs, with database RLS as a second boundary."""
    if authenticated_client is None:
        raise ValueError("An authenticated Supabase client is required.")
    try:
        user_id = str(uuid.UUID(str(verified_user_id)))
    except (TypeError, ValueError, AttributeError) as exc:
        raise ValueError("A verified signed-in user is required.") from exc
    if type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError("Limit must be between 1 and 100.")
    result = (
        authenticated_client.table("voiceover_generation_jobs")
        .select("id,status,characters,quoted_credits,created_at,updated_at")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    rows = result.data or []
    return [
        {
            "id": row["id"],
            "status": row["status"],
            "characters": row["characters"],
            "quoted_credits": row["quoted_credits"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }
        for row in rows
        if row.get("status") in ALLOWED_STATUSES
    ]
