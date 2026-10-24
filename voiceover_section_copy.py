"""Prepare an offline script section clipboard copy.

This helper never calls ElevenLabs, Supabase, or billing APIs.
"""


def section_copy_text(sections, index):
    if not isinstance(sections, list) or not 1 <= len(sections) <= 100:
        raise ValueError("No valid script sections.")
    if type(index) is not int or not 0 <= index < len(sections):
        raise ValueError("Select a valid section.")
    value = sections[index]
    if not isinstance(value, str) or not 1 <= len(value.strip()) <= 5000:
        raise ValueError("Section text must contain 1 to 5,000 characters.")
    return value.strip()
