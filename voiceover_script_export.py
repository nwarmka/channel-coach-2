"""Downloadable script exports for offline Shotcut narration workflows.

Pure, in-memory generation. No user data is stored or sent externally.
"""
from voiceover_script_drafts import serialize_script_draft
from voiceover_export_names import safe_script_export_name
import json


def build_script_export(title, sections, export_format="txt"):
    serialized = serialize_script_draft(title, sections)
    project = json.loads(serialized)
    if export_format == "json":
        filename = safe_script_export_name(project["title"], ".json")
        content = (json.dumps(project, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        media_type = "application/json"
    elif export_format == "txt":
        filename = safe_script_export_name(project["title"], ".txt")
        content = ("\n\n".join(project["sections"]) + "\n").encode("utf-8")
        media_type = "text/plain; charset=utf-8"
    else:
        raise ValueError("Choose TXT or JSON.")
    return {"filename": filename, "content": content, "media_type": media_type}
