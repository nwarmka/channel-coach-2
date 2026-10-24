"""Conservative offline validation for narration script export filenames."""
import re
import unicodedata


def safe_script_export_name(title, extension=".txt"):
    if extension not in (".txt", ".json"):
        raise ValueError("Unsupported export format.")
    if not isinstance(title, str):
        raise ValueError("A script title is required.")
    normalized = unicodedata.normalize("NFKC", title)
    # Keep export names portable across Windows, macOS, and Linux.
    stem = re.sub(r"[^a-zA-Z0-9_-]+", "_", normalized).strip("_")[:60]
    if not stem:
        stem = "voiceover_script"
    if stem.upper() in {
        "CON", "PRN", "AUX", "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }:
        stem = f"script_{stem}"
    return stem + extension
