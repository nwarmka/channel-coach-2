"""User-scoped draft project CRUD helpers.

Only pass a Supabase client bound to a verified signed-in user session.
Database RLS provides a second ownership boundary. Never use service role.
"""
import uuid
from voiceover_script_drafts import serialize_script_draft, deserialize_script_draft


def _user_uuid(user_id):
    try:
        return str(uuid.UUID(str(user_id)))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError("Sign in to access saved scripts.") from exc


def _project_uuid(project_id):
    try:
        return str(uuid.UUID(str(project_id)))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError("Invalid script project ID.") from exc


def save_script_project(client, verified_user_id, title, sections, project_id=None):
    if client is None:
        raise ValueError("An authenticated Supabase client is required.")
    user = _user_uuid(verified_user_id)
    import json
    payload = json.loads(serialize_script_draft(title, sections))
    row = {"title": payload["title"], "sections": payload["sections"],
           "schema_version": 1}
    table = client.table("voiceover_script_projects")
    if project_id is None:
        row["user_id"] = user
        response = table.insert(row).execute()
    else:
        response = (table.update(row).eq("id", _project_uuid(project_id))
                    .eq("user_id", user).execute())
    if not response.data:
        raise FileNotFoundError("Script project could not be saved.")
    return response.data[0]["id"]


def list_script_projects(client, verified_user_id, limit=50):
    if client is None:
        raise ValueError("An authenticated Supabase client is required.")
    user = _user_uuid(verified_user_id)
    if type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError("Invalid project list limit.")
    response = (client.table("voiceover_script_projects")
                .select("id,title,updated_at")
                .eq("user_id", user).order("updated_at", desc=True)
                .limit(limit).execute())
    return response.data or []


def load_script_project(client, verified_user_id, project_id):
    if client is None:
        raise ValueError("An authenticated Supabase client is required.")
    user = _user_uuid(verified_user_id)
    project = _project_uuid(project_id)
    response = (client.table("voiceover_script_projects")
                .select("id,title,sections,schema_version")
                .eq("id", project).eq("user_id", user).limit(1).execute())
    rows = response.data or []
    if len(rows) != 1:
        raise FileNotFoundError("Script project not found.")
    import json
    draft = deserialize_script_draft(json.dumps({
        "schema_version": rows[0]["schema_version"],
        "title": rows[0]["title"],
        "sections": rows[0]["sections"],
    }))
    return {"id": rows[0]["id"], **draft}
