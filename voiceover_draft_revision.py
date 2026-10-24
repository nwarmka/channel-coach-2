"""Immutable draft revision fingerprints for safe save/resume conflict detection.

A revision is computed from the canonical validated title and section order.
Callers can compare the revision last opened with the latest saved revision
before writing, avoiding silent overwrite across multiple editing sessions.
"""
import hashlib
from voiceover_script_drafts import serialize_script_draft


def script_draft_revision(title, sections):
    canonical = serialize_script_draft(title, sections)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def draft_has_conflict(opened_revision, latest_title, latest_sections):
    if not isinstance(opened_revision, str) or len(opened_revision) != 64:
        raise ValueError("A valid original revision is required.")
    try:
        bytes.fromhex(opened_revision)
    except ValueError as exc:
        raise ValueError("A valid original revision is required.") from exc
    return opened_revision != script_draft_revision(latest_title, latest_sections)
