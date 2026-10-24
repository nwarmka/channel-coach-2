"""Pure optimistic-concurrency save preparation for voiceover scripts.

The final database update must still enforce a compare-and-swap condition
atomically. A client-side check alone cannot prevent simultaneous overwrites.
"""
from voiceover_draft_revision import script_draft_revision, draft_has_conflict
from voiceover_script_drafts import validate_script_sections


class ScriptRevisionConflictError(ValueError):
    """The saved script changed since this editing session opened."""


def prepare_script_revision_update(opened_revision, latest_title,
                                   latest_sections, new_title, new_sections):
    if draft_has_conflict(opened_revision, latest_title, latest_sections):
        raise ScriptRevisionConflictError(
            "This script changed in another session. Reload before saving."
        )
    # Validate both title and sections through canonical revision calculation.
    next_revision = script_draft_revision(new_title, new_sections)
    return {
        "title": new_title.strip(),
        "sections": validate_script_sections(new_sections),
        "previous_revision": opened_revision,
        "next_revision": next_revision,
    }
