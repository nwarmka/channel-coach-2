import os
import uuid

import gradio as gr
from dotenv import load_dotenv

try:
    from supabase import create_client
except Exception:
    create_client = None

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

_bug_client = None


def _client():
    """
    Backend-only Supabase client for bug reports.

    SUPABASE_SERVICE_ROLE_KEY must stay in Render/server environment variables.
    Never expose it in browser code or commit it to GitHub.
    """
    global _bug_client

    if _bug_client is not None:
        return _bug_client

    if not create_client or not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise RuntimeError(
            "Bug reporting is not configured. Add SUPABASE_URL and "
            "SUPABASE_SERVICE_ROLE_KEY to the Render environment."
        )

    _bug_client = create_client(
        SUPABASE_URL,
        SUPABASE_SERVICE_ROLE_KEY,
    )

    return _bug_client


def _valid_user_id(user_id):
    try:
        return str(uuid.UUID(str(user_id)))
    except (ValueError, TypeError, AttributeError):
        raise ValueError("A valid signed-in user is required to submit a bug report.")


def submit_bug_report(
    page_name,
    category,
    severity,
    what_happened,
    expected_behavior,
    steps_to_reproduce,
    user_id,
):
    """
    Save a bug report to Supabase.
    """
    user_id = _valid_user_id(user_id)

    what_happened = (what_happened or "").strip()
    expected_behavior = (expected_behavior or "").strip()
    steps_to_reproduce = (steps_to_reproduce or "").strip()
    page_name = (page_name or "Other").strip()
    category = (category or "Other").strip()
    severity = (severity or "Medium").strip()

    if not what_happened:
        return (
            "❌ Please tell us what happened.",
            gr.update(),
            gr.update(),
            gr.update(),
        )

    try:
        (
            _client()
            .table("bug_reports")
            .insert({
                "user_id": user_id,
                "page_name": page_name,
                "category": category,
                "severity": severity,
                "what_happened": what_happened,
                "expected_behavior": expected_behavior,
                "steps_to_reproduce": steps_to_reproduce,
                "status": "new",
            })
            .execute()
        )

        return (
            "✅ Bug report submitted. Thank you — it has been saved for review.",
            "",
            "",
            "",
        )

    except Exception as exc:
        print(f"Bug report submission failed: {exc}", flush=True)
        return (
            "❌ I couldn't save the bug report right now. Please try again.",
            gr.update(),
            gr.update(),
            gr.update(),
        )


def build_bug_report_page(workspace_name, visible=False):
    """
    Build the in-app Channel Coach bug report page.
    """

    css = """
    #bug-report-page {
        width: 100% !important;
        max-width: 900px !important;
        margin: 0 auto !important;
        padding: 8px 0 30px !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    #bug-report-card {
        padding: 22px !important;
        background:
            radial-gradient(circle at 12% 0%, rgba(139,92,246,.12), transparent 34%),
            linear-gradient(180deg, rgba(13,17,29,.98), rgba(7,10,18,.99)) !important;
        border: 1px solid rgba(139,92,246,.46) !important;
        border-radius: 20px !important;
        box-shadow:
            0 18px 38px rgba(0,0,0,.32),
            0 0 24px rgba(139,92,246,.08) !important;
    }

    #bug-report-page h2 {
        margin-bottom: 6px !important;
        background: linear-gradient(90deg,#ff3ea5,#8b5cf6,#16d9ff);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent !important;
    }

    #bug-report-page .cc-bug-subtitle {
        color: #9aa5bd;
        margin-bottom: 18px;
    }

    #bug-submit-button {
        margin-top: 8px !important;
        min-height: 48px !important;
        background: linear-gradient(90deg,#8b5cf6,#ff3ea5) !important;
        color: white !important;
        border: none !important;
        font-weight: 900 !important;
    }

    #bug-report-status {
        margin-top: 10px !important;
    }

    #bug-report-status p {
        color: #e8ebf5 !important;
    }
    """

    with gr.Column(
        visible=visible,
        elem_id="bug-report-page",
    ) as page:

        gr.HTML(f"<style>{css}</style>")

        with gr.Column(elem_id="bug-report-card"):
            gr.HTML(
                """
                <h2>🐞 Report a Bug</h2>
                <div class="cc-bug-subtitle">
                    Tell us what went wrong so we can improve Channel Coach.
                </div>
                """
            )

            with gr.Row():
                page_name = gr.Dropdown(
                    choices=[
                        "Home / Dashboard",
                        "Coach Chat",
                        "Calendar",
                        "Toolkit",
                        "Settings",
                        "Login / Account",
                        "Credits",
                        "Other",
                    ],
                    value="Other",
                    label="Where did it happen?",
                )

                category = gr.Dropdown(
                    choices=[
                        "Something didn't work",
                        "Wrong or missing data",
                        "Layout / visual issue",
                        "Slow / performance issue",
                        "Login / account issue",
                        "Credits issue",
                        "Other",
                    ],
                    value="Something didn't work",
                    label="Type of problem",
                )

                severity = gr.Dropdown(
                    choices=[
                        "Low",
                        "Medium",
                        "High",
                        "Critical",
                    ],
                    value="Medium",
                    label="How serious is it?",
                )

            what_happened = gr.Textbox(
                label="What happened?",
                placeholder="Example: I clicked an event on the calendar and nothing opened.",
                lines=5,
            )

            expected_behavior = gr.Textbox(
                label="What did you expect to happen?",
                placeholder="Example: I expected the event editor to open.",
                lines=4,
            )

            steps_to_reproduce = gr.Textbox(
                label="How can we reproduce it? (optional)",
                placeholder=(
                    "Example:\n"
                    "1. Open Calendar\n"
                    "2. Click an event\n"
                    "3. Nothing happens"
                ),
                lines=5,
            )

            submit_button = gr.Button(
                "SUBMIT BUG REPORT",
                variant="primary",
                elem_id="bug-submit-button",
            )

            status = gr.Markdown(elem_id="bug-report-status")

            submit_button.click(
                fn=submit_bug_report,
                inputs=[
                    page_name,
                    category,
                    severity,
                    what_happened,
                    expected_behavior,
                    steps_to_reproduce,
                    workspace_name,
                ],
                outputs=[
                    status,
                    what_happened,
                    expected_behavior,
                    steps_to_reproduce,
                ],
                show_progress="hidden",
            )

    return page


