"""Bounded script section serialization for draft save/resume workflows.

Pure validation only. Persistence and per-user RLS are implemented separately.
"""
import json

MAX_SECTIONS = 100
MAX_SECTION_CHARS = 5000
MAX_PROJECT_BYTES = 600_000


def validate_script_sections(sections):
    if not isinstance(sections, list) or not 1 <= len(sections) <= MAX_SECTIONS:
        raise ValueError("A project needs between 1 and 100 sections.")
    cleaned = []
    for item in sections:
        if not isinstance(item, str):
            raise ValueError("Every section must be text.")
        text = item.strip()
        if not 1 <= len(text) <= MAX_SECTION_CHARS:
            raise ValueError("Each section must contain 1 to 5,000 characters.")
        cleaned.append(text)
    return cleaned


def serialize_script_draft(title, sections):
    if not isinstance(title, str) or not 1 <= len(title.strip()) <= 120:
        raise ValueError("Enter a project title of 1 to 120 characters.")
    payload = {"schema_version": 1, "title": title.strip(),
               "sections": validate_script_sections(sections)}
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    if len(data.encode("utf-8")) > MAX_PROJECT_BYTES:
        raise ValueError("The script project is too large.")
    return data


def deserialize_script_draft(data):
    if not isinstance(data, str) or len(data.encode("utf-8")) > MAX_PROJECT_BYTES:
        raise ValueError("Invalid project data.")
    try:
        payload = json.loads(data)
    except (TypeError, ValueError) as exc:
        raise ValueError("Invalid project data.") from exc
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ValueError("Unsupported project format.")
    return json.loads(serialize_script_draft(
        payload.get("title"), payload.get("sections")
    ))
