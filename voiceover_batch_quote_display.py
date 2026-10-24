"""Read-only batch quote summary for script editor display."""
from voiceover_batch_quote import quote_script_sections


def format_batch_quote(sections, selected_indices=None):
    quote = quote_script_sections(sections, selected_indices)
    lines = [
        f"Total: {quote['total_credits']} credits for "
        f"{quote['total_characters']} characters"
    ]
    for item in quote["sections"]:
        lines.append(
            f"Section {item['index'] + 1}: {item['credits']} credits "
            f"({item['characters']} characters)"
        )
    lines.append("Preview only. No credits charged.")
    return "\n".join(lines)
