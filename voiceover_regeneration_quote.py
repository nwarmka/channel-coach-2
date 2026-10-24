"""Pure read-only quote for regenerating just one narration clip."""
from voiceover_batch_quote import quote_script_sections


def quote_clip_regeneration(sections, section_index, previous_job_id=None):
    if type(section_index) is not int:
        raise ValueError("Choose a valid section.")
    quote = quote_script_sections(sections, [section_index])
    # Prior generation is never refunded just because a user requests a
    # different take; a new generation requires a new explicit approval.
    return {
        "section_index": section_index,
        "characters": quote["total_characters"],
        "credits": quote["total_credits"],
        "previous_job_id": previous_job_id,
        "requires_new_approval": True,
        "generation_enabled": False,
    }
