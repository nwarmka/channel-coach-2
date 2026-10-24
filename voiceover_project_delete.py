"""Draft project deletion scoped to a verified signed-in account.

Deletion is explicit, permanent, and does not remove generated audio jobs.
The caller must confirm intent in the UI before calling this function.
"""
import uuid


def delete_script_project(authenticated_client, verified_user_id, project_id):
    if authenticated_client is None:
        raise ValueError("An authenticated Supabase client is required.")
    try:
        user = str(uuid.UUID(str(verified_user_id)))
        project = str(uuid.UUID(str(project_id)))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError("Valid user and project IDs are required.") from exc
    response = (
        authenticated_client.table("voiceover_script_projects")
        .delete()
        .eq("id", project)
        .eq("user_id", user)
        .execute()
    )
    rows = response.data or []
    if len(rows) != 1 or rows[0].get("id") != project:
        raise FileNotFoundError("Script project not found or not deleted.")
    return True
