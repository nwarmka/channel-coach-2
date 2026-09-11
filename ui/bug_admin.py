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
CHANNEL_COACH_ADMIN_USER_ID = os.getenv("CHANNEL_COACH_ADMIN_USER_ID", "").strip()

_admin_client = None


def _client():
    global _admin_client

    if _admin_client is not None:
        return _admin_client

    if not create_client or not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise RuntimeError("Admin bug dashboard is not configured.")

    _admin_client = create_client(
        SUPABASE_URL,
        SUPABASE_SERVICE_ROLE_KEY,
    )
    return _admin_client


def _is_admin(user_id):
    try:
        current = str(uuid.UUID(str(user_id)))
        configured = str(uuid.UUID(CHANNEL_COACH_ADMIN_USER_ID))
        return current == configured
    except Exception:
        return False


def _render_reports(rows):
    if not rows:
        return """
        <div class="bug-admin-empty">
            No bug reports match these filters.
        </div>
        """

    cards = []

    for row in rows:
        report_id = str(row.get("id", ""))
        page_name = row.get("page_name", "Other")
        category = row.get("category", "Other")
        severity = row.get("severity", "Medium")
        status = row.get("status", "new")
        what = row.get("what_happened", "")
        expected = row.get("expected_behavior", "")
        steps = row.get("steps_to_reproduce", "")
        created = str(row.get("created_at", "")).replace("T", " ")[:19]

        cards.append(
            f"""
            <div class="bug-admin-card">
                <div class="bug-admin-top">
                    <span class="bug-admin-severity">{severity}</span>
                    <span class="bug-admin-status">{status.upper()}</span>
                    <span class="bug-admin-date">{created}</span>
                </div>

                <div class="bug-admin-meta">
                    <b>{page_name}</b> · {category}
                </div>

                <div class="bug-admin-section">
                    <span>WHAT HAPPENED</span>
                    <p>{gr.utils.sanitize_html(what) if hasattr(gr.utils, "sanitize_html") else what}</p>
                </div>

                <div class="bug-admin-section">
                    <span>EXPECTED</span>
                    <p>{gr.utils.sanitize_html(expected) if hasattr(gr.utils, "sanitize_html") else expected or "—"}</p>
                </div>

                <div class="bug-admin-section">
                    <span>STEPS</span>
                    <p>{gr.utils.sanitize_html(steps) if hasattr(gr.utils, "sanitize_html") else steps or "—"}</p>
                </div>

                <div class="bug-admin-id">
                    Report ID: {report_id}
                </div>
            </div>
            """
        )

    return "".join(cards)


def load_bug_reports(status_filter, severity_filter, user_id):
    if not _is_admin(user_id):
        return (
            """
            <div class="bug-admin-denied">
                🔒 This page is restricted to the Channel Coach administrator.
            </div>
            """,
            gr.update(choices=[], value=None),
        )

    try:
        query = (
            _client()
            .table("bug_reports")
            .select("*")
            .order("created_at", desc=True)
        )

        if status_filter and status_filter != "All":
            query = query.eq("status", status_filter.lower())

        if severity_filter and severity_filter != "All":
            query = query.eq("severity", severity_filter)

        result = query.execute()
        rows = result.data or []

        choices = [
            (
                f'{row.get("severity", "Medium")} | '
                f'{row.get("status", "new").upper()} | '
                f'{row.get("page_name", "Other")} | '
                f'{str(row.get("what_happened", ""))[:55]}',
                str(row.get("id")),
            )
            for row in rows
        ]

        return (
            _render_reports(rows),
            gr.update(choices=choices, value=None),
        )

    except Exception as exc:
        print(f"Bug dashboard load failed: {exc}", flush=True)
        return (
            "<div class='bug-admin-denied'>❌ Could not load bug reports.</div>",
            gr.update(choices=[], value=None),
        )


def update_bug_status(report_id, new_status, user_id):
    if not _is_admin(user_id):
        return "❌ Admin access required."

    if not report_id:
        return "❌ Choose a bug report first."

    status = (new_status or "").strip().lower()

    if status not in {"new", "reviewing", "fixed", "closed"}:
        return "❌ Invalid status."

    try:
        (
            _client()
            .table("bug_reports")
            .update({"status": status})
            .eq("id", report_id)
            .execute()
        )
        return f"✅ Bug report marked {status}."

    except Exception as exc:
        print(f"Bug status update failed: {exc}", flush=True)
        return "❌ Could not update that bug report."


def build_bug_admin_page(workspace_name, visible=False):
    css = """
    #bug-admin-page {
        width: 100% !important;
        max-width: 1000px !important;
        margin: 0 auto !important;
        padding: 8px 0 30px !important;
    }

    #bug-admin-page h2 {
        background: linear-gradient(90deg,#ff3ea5,#8b5cf6,#16d9ff);
        -webkit-background-clip:text;
        background-clip:text;
        color:transparent !important;
    }

    #bug-admin-list {
        margin-top: 16px !important;
    }

    .bug-admin-card {
        margin: 0 0 14px;
        padding: 18px;
        border-radius: 18px;
        background: linear-gradient(180deg,rgba(18,23,42,.98),rgba(9,12,23,.98));
        border: 1px solid rgba(139,92,246,.42);
        box-shadow: 0 12px 26px rgba(0,0,0,.25);
        color: #eef2ff;
    }

    .bug-admin-top {
        display:flex;
        gap:10px;
        align-items:center;
        flex-wrap:wrap;
        margin-bottom:10px;
    }

    .bug-admin-severity,
    .bug-admin-status {
        padding:4px 9px;
        border-radius:999px;
        font-size:11px;
        font-weight:900;
        letter-spacing:.05em;
        background:rgba(139,92,246,.18);
        border:1px solid rgba(139,92,246,.35);
    }

    .bug-admin-date {
        color:#8f9bb3;
        font-size:12px;
        margin-left:auto;
    }

    .bug-admin-meta {
        color:#cbd5e1;
        margin-bottom:14px;
    }

    .bug-admin-section {
        margin-top:12px;
        padding-top:12px;
        border-top:1px solid rgba(255,255,255,.06);
    }

    .bug-admin-section span {
        color:#22d3ee;
        font-size:10px;
        font-weight:900;
        letter-spacing:.08em;
    }

    .bug-admin-section p {
        color:#e8ebf5;
        margin:6px 0 0;
        white-space:pre-wrap;
    }

    .bug-admin-id {
        color:#6f7b93;
        font-size:10px;
        margin-top:14px;
    }

    .bug-admin-denied,
    .bug-admin-empty {
        padding:22px;
        border-radius:16px;
        background:rgba(15,23,42,.88);
        border:1px solid rgba(139,92,246,.3);
        color:#cbd5e1;
        text-align:center;
    }
    """

    with gr.Column(visible=visible, elem_id="bug-admin-page") as page:
        gr.HTML(f"<style>{css}</style>")
        gr.Markdown("## 🛠️ Bug Dashboard")
        gr.Markdown("Review tester reports and update their status.")

        with gr.Row():
            status_filter = gr.Dropdown(
                choices=["All", "New", "Reviewing", "Fixed", "Closed"],
                value="All",
                label="Status",
            )
            severity_filter = gr.Dropdown(
                choices=["All", "Low", "Medium", "High", "Critical"],
                value="All",
                label="Severity",
            )
            refresh_button = gr.Button("↻ Refresh")

        report_list = gr.HTML(
            "<div class='bug-admin-empty'>Open this page to load reports.</div>",
            elem_id="bug-admin-list",
        )

        gr.Markdown("### Update a report")
        report_picker = gr.Dropdown(
            choices=[],
            label="Bug report",
        )
        new_status = gr.Dropdown(
            choices=["New", "Reviewing", "Fixed", "Closed"],
            value="Reviewing",
            label="New status",
        )
        update_button = gr.Button("UPDATE STATUS", variant="primary")
        update_message = gr.Markdown()

        refresh_button.click(
            load_bug_reports,
            inputs=[status_filter, severity_filter, workspace_name],
            outputs=[report_list, report_picker],
            show_progress="hidden",
        )

        status_filter.change(
            load_bug_reports,
            inputs=[status_filter, severity_filter, workspace_name],
            outputs=[report_list, report_picker],
            show_progress="hidden",
        )

        severity_filter.change(
            load_bug_reports,
            inputs=[status_filter, severity_filter, workspace_name],
            outputs=[report_list, report_picker],
            show_progress="hidden",
        )

        update_button.click(
            update_bug_status,
            inputs=[report_picker, new_status, workspace_name],
            outputs=[update_message],
            show_progress="hidden",
        ).then(
            load_bug_reports,
            inputs=[status_filter, severity_filter, workspace_name],
            outputs=[report_list, report_picker],
            show_progress="hidden",
        )

    return page

