"""Voiceover Studio UI draft.

Not wired into app.py yet. Audio generation remains disabled until authenticated
credit authorization, cost approval, and storage handling are implemented.
"""
import re
import gradio as gr
from elevenlabs_service import list_voices, ElevenLabsError
from voiceover_pricing import quote_voiceover_credits


def split_script(script):
    """Split on blank lines, preserving paragraph text as editable sections."""
    text = (script or "").strip()
    if not text:
        return [], gr.update(choices=[], value=None), "", "Enter a script first."
    parts = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if len(parts) > 100:
        return [], gr.update(choices=[], value=None), "", "Limit scripts to 100 sections."
    choices = [(f"Section {i + 1}: {p[:55]}", str(i)) for i, p in enumerate(parts)]
    return parts, gr.update(choices=choices, value="0"), parts[0], f"{len(parts)} editable sections ready."


def select_section(section_id, sections):
    try:
        return sections[int(section_id)]
    except (ValueError, TypeError, IndexError):
        return ""


def save_section(section_id, updated_text, sections):
    updated = (updated_text or "").strip()
    if not updated:
        return sections, gr.update(), "A section cannot be empty."
    try:
        index = int(section_id)
        new_sections = list(sections)
        new_sections[index] = updated
    except (ValueError, TypeError, IndexError):
        return sections, gr.update(), "Select a section first."
    choices = [(f"Section {i + 1}: {p[:55]}", str(i)) for i, p in enumerate(new_sections)]
    return new_sections, gr.update(choices=choices, value=str(index)), "Section saved."


def move_section(section_id, sections, direction):
    try:
        index = int(section_id)
        other = index + direction
        if not 0 <= other < len(sections):
            return sections, gr.update(), "Section is already at the end."
        new_sections = list(sections)
        new_sections[index], new_sections[other] = new_sections[other], new_sections[index]
        choices = [(f"Section {i + 1}: {p[:55]}", str(i)) for i, p in enumerate(new_sections)]
        return new_sections, gr.update(choices=choices, value=str(other)), "Section moved."
    except (ValueError, TypeError, IndexError):
        return sections, gr.update(), "Select a section first."


def load_voice_choices():
    """Retrieve available voices on demand; never expose the API key."""
    try:
        voices = list_voices()
        choices = [(voice["name"], voice["voice_id"]) for voice in voices]
        return gr.update(choices=choices, value=None), (
            f"Loaded {len(choices)} available voices." if choices else
            "No voices available for this ElevenLabs account."
        )
    except ElevenLabsError as exc:
        return gr.update(choices=[], value=None), str(exc)


def preview_section_usage(section_id, sections):
    """Show character usage without charging credits or calling ElevenLabs.

    Credit pricing must be configured and validated against provider costs
    before generation can be enabled.
    """
    try:
        text = sections[int(section_id)]
    except (ValueError, TypeError, IndexError):
        return "Select a script section to see its estimated usage."
    characters = len(text)
    if characters > 5000:
        return f"⚠️ {characters:,} characters. Shorten this section to 5,000 characters or less."
    return (
        f"Selected section: **{characters:,} characters**. "
        "Channel Coach credit cost: **not configured yet**. "
        "No credits have been charged."
    )


def quote_selected_section(section_id, sections):
    """Display a non-binding quote; no credits are spent here."""
    try:
        text = sections[int(section_id)]
        quote = quote_voiceover_credits(text)
    except (ValueError, TypeError, IndexError) as exc:
        return f"Cannot quote section: {exc}"
    except RuntimeError:
        return "Voiceover pricing is not configured correctly."
    if quote is None:
        return (
            "Voiceover credit price is not available yet. "
            "Generation remains disabled until pricing is approved."
        )
    return (
        f"**Estimated cost: {quote['credits']:,} Channel Coach credits** "
        f"for {quote['characters']:,} characters. "
        "This is a preview only; no credits have been deducted."
    )


def build_voiceover_page(visible=False):
    """Build draft editor; generation intentionally unavailable."""
    with gr.Column(visible=visible, elem_id="voiceover-studio-page") as page:
        gr.Markdown("## 🎙️ AI Script & Voiceover Studio")
        gr.Markdown("Draft and arrange narration sections. Audio generation is coming soon.")
        with gr.Row():
            refresh_voices = gr.Button("Load available voices")
            voice = gr.Dropdown(label="Narrator voice", choices=[], interactive=True)
        voice_status = gr.Markdown()
        usage = gr.Markdown("Select a section to see its character usage.")
        gr.Markdown("**MP3 generation is disabled until credit pricing, authentication, and safe storage are ready.**")
        refresh_voices.click(load_voice_choices, outputs=[voice, voice_status])
        sections = gr.State([])
        script = gr.Textbox(label="Your script", lines=10, placeholder="Paste your script here. Separate sections with blank lines.")
        split = gr.Button("Split into sections")
        selected = gr.Dropdown(label="Script sections", choices=[], interactive=True)
        editor = gr.Textbox(label="Edit selected section", lines=5)
        with gr.Row():
            save = gr.Button("Save section")
            up = gr.Button("Move up")
            down = gr.Button("Move down")
        status = gr.Markdown()
        quote_button = gr.Button("Check credit cost")
        quote_result = gr.Markdown("No quote requested yet.")
        quote_button.click(quote_selected_section, inputs=[selected, sections], outputs=[quote_result])
        split.click(split_script, inputs=[script], outputs=[sections, selected, editor, status])
        selected.change(select_section, inputs=[selected, sections], outputs=[editor])
        save.click(save_section, inputs=[selected, editor, sections], outputs=[sections, selected, status])
        up.click(lambda idx, parts: move_section(idx, parts, -1), inputs=[selected, sections], outputs=[sections, selected, status])
        down.click(lambda idx, parts: move_section(idx, parts, 1), inputs=[selected, sections], outputs=[sections, selected, status])
        selected.change(preview_section_usage, inputs=[selected, sections], outputs=[usage])
        save.click(preview_section_usage, inputs=[selected, sections], outputs=[usage])
    return page
