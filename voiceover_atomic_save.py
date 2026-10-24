"""Optimistic-concurrency script save through a single database RPC.

The SQL RPC must be reviewed and deployed first. The caller must provide a
session-authenticated Supabase client; never use a service-role client here.
"""
import uuid
from voiceover_revision_update import prepare_script_revision_update


def save_script_if_unchanged(client, verified_user_id, project_id,
                             opened_revision, latest_title, latest_sections,
                             new_title, new_sections):
    if client is None:
        raise ValueError("An authenticated Supabase client is required.")
    try:
        user = str(uuid.UUID(str(verified_user_id)))
        project = str(uuid.UUID(str(project_id)))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError("Valid user and project IDs are required.") from exc
    if not user:
        raise ValueError("Sign in before saving.")
    prepared = prepare_script_revision_update(
        opened_revision, latest_title, latest_sections, new_title, new_sections
    )
    response = client.rpc("update_voiceover_script_project_if_revision", {
        "p_project_id": project,
        "p_previous_revision": prepared["previous_revision"],
        "p_title": prepared["title"],
        "p_sections": prepared["sections"],
        "p_next_revision": prepared["next_revision"],
    }).execute()
    if response.data is not True:
        raise RuntimeError(
            "The script changed or is no longer accessible. Reload before saving."
        )
    return prepared["next_revision"]
