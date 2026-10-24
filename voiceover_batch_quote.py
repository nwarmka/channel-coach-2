"""Pure voiceover section selection for batch narration planning.

Planning only: no ElevenLabs calls, billing, or storage writes.
"""
from voiceover_pricing import quote_voiceover_credits


def quote_script_sections(sections, selected_indices=None):
    if not isinstance(sections, list) or not 1 <= len(sections) <= 100:
        raise ValueError("A script needs 1 to 100 sections.")
    if selected_indices is None:
        selected_indices = list(range(len(sections)))
    if not isinstance(selected_indices, list) or not selected_indices:
        raise ValueError("Select at least one section.")
    if any(type(index) is not int for index in selected_indices):
        raise ValueError("Section indexes must be integers.")
    if len(selected_indices) != len(set(selected_indices)):
        raise ValueError("Duplicate section selection.")
    if any(index < 0 or index >= len(sections) for index in selected_indices):
        raise ValueError("Selected section does not exist.")
    quotes = []
    for index in selected_indices:
        quote = quote_voiceover_credits(sections[index])
        quotes.append({
            "index": index,
            "characters": quote["characters"],
            "credits": quote["credits"],
        })
    return {
        "sections": quotes,
        "total_characters": sum(item["characters"] for item in quotes),
        "total_credits": sum(item["credits"] for item in quotes),
    }
