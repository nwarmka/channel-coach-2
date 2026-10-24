"""Voiceover Studio UI draft.

Integrated into app.py on the development branch. Audio generation remains disabled until authenticated
credit authorization, cost approval, and storage handling are implemented.
"""
import re
import gradio as gr
from elevenlabs_service import list_voices, ElevenLabsError
from voiceover_pricing import quote_voiceover_credits
from voiceover_quote import create_quote_snapshot, quote_is_current
from voiceover_section_copy import section_copy_text
from voiceover_regeneration_quote import quote_clip_regeneration
from voiceover_batch_quote_display import format_batch_quote
from voiceover_batch_quote import quote_script_sections
from voiceover_script_export import build_script_export
from voiceover_jobs import list_voiceover_jobs
from voiceover_job_display import summarize_voiceover_jobs
from ui.ideas_inbox import _authenticated_client


def split_script(script):
    """Split on blank lines, preserving paragraph text as editable sections."""
    text = (script or "").strip()
    if not text:
        return [], gr.update(choices=[], value=None), "", "Enter a script first."
    parts = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if len(parts) > 100:
        return [], gr.update(choices=[], value=None), "", "Limit scripts to 100 sections."
    if any(len(part) > 5000 for part in parts):
        return [], gr.update(choices=[], value=None), "", "Each section must be 5,000 characters or less."
    choices = [(f"Section {i + 1}: {p[:55]}", str(i)) for i, p in enumerate(parts)]
    return parts, gr.update(choices=choices, value="0"), parts[0], f"{len(parts)} editable sections ready."


def select_section(section_id, sections):
    try:
        index = int(section_id)
        return sections[index] if 0 <= index < len(sections) else ""
    except (ValueError, TypeError, IndexError):
        return ""


def save_section(section_id, updated_text, sections):
    updated = (updated_text or "").strip()
    if not updated:
        return sections, gr.update(), "A section cannot be empty."
    if len(updated) > 5000:
        return sections, gr.update(), "A section cannot exceed 5,000 characters."
    try:
        index = int(section_id)
        new_sections = list(sections)
        if not 0 <= index < len(new_sections):
            raise IndexError("Invalid section")
        new_sections[index] = updated
    except (ValueError, TypeError, IndexError):
        return sections, gr.update(), "Select a section first."
    choices = [(f"Section {i + 1}: {p[:55]}", str(i)) for i, p in enumerate(new_sections)]
    return new_sections, gr.update(choices=choices, value=str(index)), "Section saved."


def move_section(section_id, sections, direction):
    try:
        index = int(section_id)
        other = index + direction
        if not 0 <= index < len(sections):
            raise IndexError("Invalid section")
        if not 0 <= other < len(sections):
            return sections, gr.update(), "Section is already at the beginning." if direction < 0 else "Section is already at the end."
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
        index = int(section_id)
        if not 0 <= index < len(sections):
            raise IndexError("Invalid section")
        text = sections[index]
    except (ValueError, TypeError, IndexError):
        return "Select a script section to see its estimated usage."
    characters = len(text)
    if characters > 5000:
        return f"⚠️ {characters:,} characters. Shorten this section to 5,000 characters or less."
    return (
        f"Selected section: **{characters:,} characters**. "
        "Use Check credit cost for a quote. "
        "No credits have been charged."
    )


def quote_selected_section(section_id, sections, voice_id):
    """Return a read-only quote and snapshot; never charge or generate."""
    try:
        index = int(section_id)
        if not 0 <= index < len(sections):
            raise IndexError("Invalid section")
        text = sections[index]
        quote = quote_voiceover_credits(text)
        snapshot = create_quote_snapshot(str(index), text, voice_id)
    except (ValueError, TypeError, IndexError, AttributeError) as exc:
        return f"Cannot quote section: {exc}", None
    return (
        f"**Estimated cost: {quote['credits']:,} Channel Coach credits** "
        f"for {quote['characters']:,} characters. "
        "Review this quote before confirming. No credits have been deducted."
    ), snapshot


def confirm_quote(section_id, sections, voice_id, snapshot):
    """Confirm an unchanged quote; generation remains disabled."""
    try:
        index = int(section_id)
        if not 0 <= index < len(sections):
            raise IndexError("Invalid section")
        valid = quote_is_current(snapshot, str(index), sections[index], voice_id)
    except (ValueError, TypeError, IndexError):
        valid = False
    if not valid:
        return "The quote is missing or the section, text, voice, or price changed. Request a new quote."
    return (
        f"Quote confirmed for {snapshot['credits']} credits. "
        "Generation is not enabled yet; no credits were charged."
    )


def refresh_voiceover_history(saved_session):
    """Read only the verified user's jobs; never disclose private storage paths."""
    try:
        client, user_id, updated = _authenticated_client(saved_session)
        jobs = summarize_voiceover_jobs(list_voiceover_jobs(client, user_id))
        if not jobs:
            return [], "No voiceover jobs yet.", updated
        rows = [
            [job["created_at"][:19], job["status"],
             job["characters"], job["quoted_credits"]]
            for job in jobs
        ]
        return rows, f"Loaded {len(rows)} voiceover jobs.", updated
    except ValueError:
        return [], "Sign in to view your voiceover history.", saved_session
    except Exception as exc:
        print("Voiceover history refresh error:", type(exc).__name__)
        return [], "Voiceover history is not available yet.", saved_session


def export_script_file(title, sections, export_format):
    """Create an offline script export without generation or credit charges."""
    import tempfile
    from pathlib import Path
    try:
        artifact = build_script_export(title, sections, export_format)
        directory = Path(tempfile.mkdtemp(prefix="cc_script_export_"))
        path = directory / artifact["filename"]
        path.write_bytes(artifact["content"])
        return str(path), "Script export ready. No credits charged."
    except (ValueError, TypeError) as exc:
        return None, f"Cannot export script: {exc}"


def quote_full_script(sections):
    """Preview the complete section-by-section cost without any billing."""
    try:
        return format_batch_quote(sections)
    except (ValueError, TypeError) as exc:
        return f"Cannot quote script: {exc}"


def preview_clip_regeneration(section_id, sections):
    """Read-only preview; no new audio job or charge is created."""
    try:
        quote = quote_clip_regeneration(sections, int(section_id))
    except (ValueError, TypeError, IndexError) as exc:
        return f"Cannot quote clip regeneration: {exc}"
    return (
        f"**Regenerate section {quote['section_index'] + 1}: "
        f"{quote['credits']} credits** for {quote['characters']} characters. "
        "A fresh approval will be required. "
        "Regeneration is not enabled yet; no credits charged."
    )


def prepare_section_copy(section_id, sections):
    """Show a validated section in a copy-friendly text field."""
    try:
        return section_copy_text(sections, int(section_id)), "Section ready to copy."
    except (ValueError, TypeError, IndexError) as exc:
        return "", f"Cannot copy section: {exc}"


def add_script_section(sections):
    """Append an editable section without modifying stored projects."""
    from voiceover_section_editor import append_script_section
    try:
        updated = append_script_section(sections, "New section")
    except (ValueError, TypeError) as exc:
        return sections, gr.update(), "", f"Cannot add section: {exc}"
    index = len(updated) - 1
    choices = [(f"Section {i + 1}: {p[:55]}", str(i)) for i, p in enumerate(updated)]
    return updated, gr.update(choices=choices, value=str(index)), updated[index], "Section added."


def delete_script_section(section_id, sections):
    """Delete only the selected in-memory section, never a stored project."""
    from voiceover_section_editor import remove_script_section
    try:
        updated = remove_script_section(sections, int(section_id))
    except (ValueError, TypeError, IndexError) as exc:
        return sections, gr.update(), "", f"Cannot delete section: {exc}"
    choices = [(f"Section {i + 1}: {p[:55]}", str(i)) for i, p in enumerate(updated)]
    index = min(int(section_id), len(updated) - 1)
    return updated, gr.update(choices=choices, value=str(index) if updated else None), (
        updated[index] if updated else ""), "Section deleted from the current draft."


def save_new_script_draft(saved_session, title, sections):
    """Create a private new project only; existing-project updates require CAS."""
    from voiceover_project_store import save_script_project
    try:
        client, user_id, updated = _authenticated_client(saved_session)
        project_id = save_script_project(client, user_id, title, sections)
        return project_id, "New script project saved.", updated
    except ValueError as exc:
        return "", f"Cannot save project: {exc}", saved_session
    except Exception as exc:
        print("Voiceover draft save unavailable:", type(exc).__name__)
        return "", "Project saving is unavailable until the private database table is deployed.", saved_session


def refresh_saved_script_drafts(saved_session):
    """List only the authenticated user's projects; no service-role access."""
    from voiceover_project_store import list_script_projects
    try:
        client, user_id, updated = _authenticated_client(saved_session)
        projects = list_script_projects(client, user_id)
        choices = [(p["title"], p["id"]) for p in projects]
        return gr.update(choices=choices, value=None), f"Found {len(choices)} saved projects.", updated
    except ValueError:
        return gr.update(choices=[], value=None), "Sign in to see saved projects.", saved_session
    except Exception as exc:
        print("Voiceover draft listing unavailable:", type(exc).__name__)
        return gr.update(choices=[], value=None), "Saved projects are not available yet.", saved_session


def open_saved_script_draft(saved_session, project_id):
    """Open an owned project into the in-memory editor without overwriting it."""
    from voiceover_project_store import load_script_project
    try:
        client, user_id, updated = _authenticated_client(saved_session)
        project = load_script_project(client, user_id, project_id)
        sections = project["sections"]
        choices = [(f"Section {i + 1}: {p[:55]}", str(i)) for i, p in enumerate(sections)]
        return (project["title"], sections, gr.update(choices=choices, value="0"),
                sections[0], "Project opened. Save as a new project to keep changes.", updated)
    except (ValueError, FileNotFoundError):
        return "", [], gr.update(choices=[], value=None), "", "Project not found or access denied.", saved_session
    except Exception as exc:
        print("Voiceover draft load unavailable:", type(exc).__name__)
        return "", [], gr.update(choices=[], value=None), "", "Saved project could not be loaded.", saved_session


def build_voiceover_page(saved_login=None, visible=False):
    """Build draft editor; generation intentionally unavailable."""
    with gr.Column(visible=visible, elem_id="voiceover-studio-page") as page:
        gr.Markdown("## 🎙️ AI Script & Voiceover Studio")
        gr.Markdown("Draft and arrange narration sections. Audio generation is coming soon.")
        gr.Markdown("**Preview release:** Script editing and exports are available. Saving projects requires the private database migration. Voice generation and credit charging are not active.")
        with gr.Row():
            refresh_voices = gr.Button("Load available voices")
            voice = gr.Dropdown(label="Narrator voice", choices=[], interactive=True)
        voice_status = gr.Markdown()
        usage = gr.Markdown("Select a section to see its character usage.")
        gr.Markdown("**MP3 generation is disabled.** A paid ElevenLabs plan with commercial rights, authenticated credit approval, and safe storage are required before launch.")
        if saved_login is not None:
            gr.Markdown("### Voiceover job history")
            history_refresh = gr.Button("Refresh job history")
            history_table = gr.Dataframe(
                headers=["Created", "Status", "Characters", "Quoted credits"],
                datatype=["str", "str", "number", "number"],
                interactive=False,
                value=[],
            )
            history_status = gr.Markdown("Refresh to load your private job history.")
            history_refresh.click(
                refresh_voiceover_history, inputs=[saved_login],
                outputs=[history_table, history_status, saved_login],
                show_progress="minimal",
            )
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
            add_section = gr.Button("Add section")
            delete_section = gr.Button("Delete selected section")
        gr.Markdown("### Your script project")
        export_title = gr.Textbox(label="Project title", value="My voiceover script")
        if saved_login is not None:
            gr.Markdown("### Private saved script projects")
            gr.Markdown("Saving creates a new copy. Existing-project overwrites are disabled until conflict-safe database updates are deployed.")
            with gr.Row():
                save_project_button = gr.Button("Save as new project")
                refresh_projects_button = gr.Button("Refresh saved projects")
            saved_project_id = gr.Textbox(label="New project ID", interactive=False)
            saved_projects = gr.Dropdown(label="Saved projects", choices=[], interactive=True)
            open_project_button = gr.Button("Open selected saved project")
            saved_project_status = gr.Markdown()
            save_project_button.click(
                save_new_script_draft,
                inputs=[saved_login, export_title, sections],
                outputs=[saved_project_id, saved_project_status, saved_login],
            )
            refresh_projects_button.click(
                refresh_saved_script_drafts,
                inputs=[saved_login],
                outputs=[saved_projects, saved_project_status, saved_login],
            )
            open_project_button.click(
                open_saved_script_draft,
                inputs=[saved_login, saved_projects],
                outputs=[export_title, sections, selected, editor, saved_project_status, saved_login],
            )
        gr.Markdown("### Export your script")
        export_format = gr.Dropdown(label="Export format", choices=["txt", "json"], value="txt")
        export_button = gr.Button("Prepare script download")
        export_file = gr.File(label="Download script", interactive=False)
        export_status = gr.Markdown()
        export_button.click(export_script_file,
                            inputs=[export_title, sections, export_format],
                            outputs=[export_file, export_status])
        copy_button = gr.Button("Prepare selected section to copy")
        copy_text = gr.Textbox(label="Copy selected narration text", lines=4,
                               interactive=True)
        copy_status = gr.Markdown()
        copy_button.click(prepare_section_copy, inputs=[selected, sections],
                          outputs=[copy_text, copy_status])
        status = gr.Markdown()
        whole_script_quote = gr.Button("Check entire script credit cost")
        whole_script_quote_result = gr.Markdown("No full-script quote requested.")
        whole_script_quote.click(quote_full_script, inputs=[sections],
                                 outputs=[whole_script_quote_result])
        regenerate_preview = gr.Button("Preview cost to regenerate selected clip")
        regenerate_result = gr.Markdown("No regeneration quote requested.")
        regenerate_preview.click(preview_clip_regeneration,
                                 inputs=[selected, sections],
                                 outputs=[regenerate_result])
        quote_snapshot = gr.State(None)
        quote_button = gr.Button("Check credit cost")
        quote_result = gr.Markdown("No quote requested yet.")
        quote_button.click(quote_selected_section, inputs=[selected, sections, voice], outputs=[quote_result, quote_snapshot])
        confirm_button = gr.Button("Confirm quote (no charge)")
        confirm_button.click(confirm_quote, inputs=[selected, sections, voice, quote_snapshot], outputs=[quote_result])
        split.click(split_script, inputs=[script], outputs=[sections, selected, editor, status])
        selected.change(select_section, inputs=[selected, sections], outputs=[editor])
        add_section.click(add_script_section, inputs=[sections], outputs=[sections, selected, editor, status])
        delete_section.click(delete_script_section, inputs=[selected, sections], outputs=[sections, selected, editor, status])
        save.click(save_section, inputs=[selected, editor, sections], outputs=[sections, selected, status])
        up.click(lambda idx, parts: move_section(idx, parts, -1), inputs=[selected, sections], outputs=[sections, selected, status])
        down.click(lambda idx, parts: move_section(idx, parts, 1), inputs=[selected, sections], outputs=[sections, selected, status])
        selected.change(preview_section_usage, inputs=[selected, sections], outputs=[usage])
        save.click(preview_section_usage, inputs=[selected, sections], outputs=[usage])
    return page
