"""Bug-report page for Channel Coach.

This module is intentionally self-contained so importing it from app.py
cannot create a circular import. The public function used by the application
is build_bug_report_page.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

import gradio as gr


def _workspace_value(workspace_name: Any) -> str:
    """Return a plain workspace name from either a string or Gradio state."""
    value = getattr(workspace_name, "value", workspace_name)
    return str(value or "Unknown workspace").strip()


def _save_bug_report(
    workspace_name: Any,
    title: str,
    category: str,
    priority: str,
    description: str,
    steps_to_reproduce: str,
) -> str:
    title = (title or "").strip()
    description = (description or "").strip()

    if not title:
        return "⚠️ Please enter a short title for the bug."

    if not description:
        return "⚠️ Please describe what went wrong."

    supabase_url = (os.getenv("SUPABASE_URL") or "").rstrip("/")
    supabase_key = (
        os.getenv("SUPABASE_KEY")
        or os.getenv("SUPABASE_ANON_KEY")
        or ""
    )

    if not supabase_url or not supabase_key:
        return "❌ Bug report was not saved because Supabase is not configured."

    payload = {
        "workspace_name": _workspace_value(workspace_name),
        "title": title,
        "category": category or "Other",
        "priority": priority or "Normal",
        "description": description,
        "steps_to_reproduce": (steps_to_reproduce or "").strip(),
        "status": "Open",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    request = urllib.request.Request(
        f"{supabase_url}/rest/v1/bug_reports",
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            if 200 <= response.status < 300:
                return "✅ Bug report submitted. Thank you!"

            return f"❌ Supabase returned status {response.status}."

    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")

        print(
            f"Bug report submission failed ({exc.code}): {details}",
            flush=True,
        )

        return (
            "❌ The report could not be saved. "
            "Please check the bug_reports table and its permissions."
        )

    except Exception as exc:
        print(f"Bug report submission failed: {exc}", flush=True)
        return "❌ The report could not be saved. Please try again."


def build_bug_report_page(
    workspace_name: Any,
    visible: bool = False,
):
    """Build and return the Channel Coach bug-report page."""

    with gr.Column(visible=visible) as page:
        workspace_input = (
            workspace_name
            if hasattr(workspace_name, "_id")
            else gr.State(value=_workspace_value(workspace_name))
        )

        gr.Markdown("## 🐞 Report a Bug")

        gr.Markdown(
            "Tell us what happened so we can investigate it. "
            "Please do not include passwords or other sensitive information."
        )

        title = gr.Textbox(
            label="Bug title",
            placeholder="Example: Calendar event does not open",
        )

        with gr.Row():
            category = gr.Dropdown(
                choices=[
                    "Calendar",
                    "Dashboard",
                    "Chat",
                    "Login / Account",
                    "Navigation",
                    "Other",
                ],
                value="Other",
                label="Area",
            )

            priority = gr.Dropdown(
                choices=[
                    "Low",
                    "Normal",
                    "High",
                    "Critical",
                ],
                value="Normal",
                label="Priority",
            )

        description = gr.Textbox(
            label="What happened?",
            placeholder=(
                "Describe what you expected and what happened instead."
            ),
            lines=5,
        )

        steps = gr.Textbox(
            label="Steps to reproduce (optional)",
            placeholder=(
                "1. Open the calendar\n"
                "2. Click an event\n"
                "3. Nothing happens"
            ),
            lines=4,
        )

        submit_button = gr.Button(
            "Submit bug report",
            variant="primary",
        )

        result = gr.Markdown()

        submit_button.click(
            fn=_save_bug_report,
            inputs=[
                workspace_input,
                title,
                category,
                priority,
                description,
                steps,
            ],
            outputs=result,
        )

    return page


__all__ = ["build_bug_report_page"]

print(
    "Loaded ui.bug_report with build_bug_report_page",
    flush=True,
)


