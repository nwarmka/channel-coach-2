# Channel Coach - Content Calendar UI

import calendar as pycalendar
from datetime import date

import gradio as gr

from features import (
    CONTENT_TYPES,
    CONTENT_STATUSES,
    add_content_item,
    delete_content_item,
    get_calendar_choices,
    load_selected_content_item,
    plan_my_week,
    refresh_content_calendar,
    render_content_calendar,
    render_upcoming_content,
    update_content_item,
)


def _month_heading(month, year):
    return f"## {pycalendar.month_name[int(month)]} {int(year)}"


def _move_month(workspace_name, month, year, status_filter, type_filter, delta):
    month = int(month)
    year = int(year)
    month += delta
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    calendar_html, upcoming_html = refresh_content_calendar(
        workspace_name, month, year, status_filter, type_filter
    )
    return month, year, _month_heading(month, year), calendar_html, upcoming_html


def _previous_month(workspace_name, month, year, status_filter, type_filter):
    return _move_month(workspace_name, month, year, status_filter, type_filter, -1)


def _next_month(workspace_name, month, year, status_filter, type_filter):
    return _move_month(workspace_name, month, year, status_filter, type_filter, 1)


def _today_month(workspace_name, status_filter, type_filter):
    today = date.today()
    calendar_html, upcoming_html = refresh_content_calendar(
        workspace_name, today.month, today.year, status_filter, type_filter
    )
    return (
        today.month,
        today.year,
        _month_heading(today.month, today.year),
        calendar_html,
        upcoming_html,
    )


def build_calendar_page(workspace_name, visible=False):
    """Build the Content Calendar page and wire all Calendar events."""

    today = date.today()

    with gr.Column(visible=visible, elem_id="calendar-page") as calendar_page:
        gr.HTML(
            """
            <style>
              #calendar-page {
                  max-width: 1280px;
                  margin: 0 auto;
              }

              #calendar-page .cc-calendar-title { margin-bottom: 2px; }
              #calendar-page .cc-calendar-subtitle {
                  opacity: .72;
                  margin-bottom: 18px;
              }

              #calendar-page .cc-card,
              #calendar-page .cc-toolbar {
                  border: 1px solid rgba(255,62,165,.32);
                  border-radius: 16px;
                  background: rgba(7,10,17,.88);
              }

              #calendar-page .cc-card { padding: 18px; }
              #calendar-page .cc-toolbar {
                  padding: 12px 14px;
                  margin-bottom: 14px;
              }

              #calendar-page .cc-calendar-main { min-height: 560px; }

              #calendar-page .cc-month-heading h2 {
                  margin: 0;
                  line-height: 1.2;
              }

              #calendar-page .cc-nav-row {
                  align-items: center;
                  gap: 8px;
              }

              #calendar-page .cc-nav-button { min-width: 46px; }
              #calendar-page .cc-today-button { min-width: 90px; }

              #calendar-page .cc-section-note {
                  opacity: .68;
                  margin-top: -6px;
                  margin-bottom: 12px;
              }

              @media (max-width: 760px) {
                  #calendar-page .cc-calendar-main { min-height: 420px; }
              }
            </style>

            <div class="cc-calendar-title">
                <h2>📅 Content Calendar</h2>
            </div>
            <div class="cc-calendar-subtitle">
                Plan long videos, Shorts, Reels, TikToks, livestreams, and community posts.
            </div>
            """
        )

        calendar_month = gr.State(today.month)
        calendar_year = gr.State(today.year)

        with gr.Row(elem_classes=["cc-toolbar", "cc-nav-row"]):
            calendar_prev_button = gr.Button("←", elem_classes=["cc-nav-button"])
            calendar_today_button = gr.Button("Today", elem_classes=["cc-today-button"])
            calendar_next_button = gr.Button("→", elem_classes=["cc-nav-button"])
            month_heading = gr.Markdown(
                _month_heading(today.month, today.year),
                elem_classes=["cc-month-heading"],
            )

            calendar_status_filter = gr.Dropdown(
                ["All"] + CONTENT_STATUSES,
                value="All",
                label="Status",
                elem_classes=["cc-cyber-field"],
                scale=1,
            )
            calendar_type_filter = gr.Dropdown(
                ["All"] + CONTENT_TYPES,
                value="All",
                label="Type",
                elem_classes=["cc-cyber-field"],
                scale=1,
            )

        with gr.Column(elem_classes=["cc-card", "cc-calendar-main"]):
            calendar_output = gr.HTML(
                value=render_content_calendar(
                    today.month, today.year, "All", "All", user_id="main"
                )
            )

        gr.Markdown(
            "### Content tools\nAdd something new, update an existing item, or let Channel Coach plan your week."
        )

        with gr.Row(equal_height=False):
            with gr.Column(scale=1, min_width=300, elem_classes=["cc-card"]):
                gr.Markdown("### ➕ Add Content")

                calendar_title = gr.Textbox(
                    label="Title",
                    placeholder="Example: Getting the Ice Rod",
                    elem_classes=["cc-cyber-field"],
                )
                calendar_content_type = gr.Dropdown(
                    CONTENT_TYPES,
                    value="Long Video",
                    label="Content Type",
                    elem_classes=["cc-cyber-field"],
                )
                calendar_game_topic = gr.Textbox(
                    label="Game / Topic",
                    placeholder="Example: Zelda ALTTP",
                    elem_classes=["cc-cyber-field"],
                )
                calendar_status = gr.Dropdown(
                    CONTENT_STATUSES,
                    value="Idea",
                    label="Status",
                    elem_classes=["cc-cyber-field"],
                )
                calendar_publish_date = gr.Textbox(
                    label="Target Publish Date",
                    value=today.isoformat(),
                    placeholder="YYYY-MM-DD",
                    elem_classes=["cc-cyber-field"],
                )
                calendar_notes = gr.Textbox(
                    label="Notes",
                    lines=4,
                    placeholder="Example: Need thumbnail, voiceover, and final export.",
                    elem_classes=["cc-cyber-field"],
                )

                calendar_add_button = gr.Button("➕ Add to Calendar")
                calendar_message = gr.Textbox(
                    show_label=False,
                    placeholder="Calendar status",
                    lines=2,
                    elem_classes=["cc-cyber-field"],
                )

            with gr.Column(scale=1, min_width=300, elem_classes=["cc-card"]):
                gr.Markdown("### 🔥 Coming Up")
                upcoming_output = gr.HTML(value=render_upcoming_content(user_id="main"))

                plan_week_button = gr.Button("✨ Plan My Week")
                plan_week_output = gr.Textbox(
                    show_label=False,
                    placeholder="Weekly content plan",
                    lines=12,
                    elem_classes=["cc-cyber-field"],
                )

        gr.Markdown("### ✏️ Edit or Delete Content")
        with gr.Column(elem_classes=["cc-card"]):
            calendar_item_picker = gr.Dropdown(
                choices=get_calendar_choices("main"),
                label="Choose Calendar Item",
                elem_classes=["cc-cyber-field"],
            )
            calendar_load_button = gr.Button("📂 Load Selected Item")
            with gr.Row():
                calendar_update_button = gr.Button("💾 Save Edit")
                calendar_delete_button = gr.Button("🗑️ Delete Selected Item")

        refresh_inputs = [
            workspace_name,
            calendar_month,
            calendar_year,
            calendar_status_filter,
            calendar_type_filter,
        ]

        nav_outputs = [
            calendar_month,
            calendar_year,
            month_heading,
            calendar_output,
            upcoming_output,
        ]

        calendar_prev_button.click(
            _previous_month,
            inputs=refresh_inputs,
            outputs=nav_outputs,
        )
        calendar_next_button.click(
            _next_month,
            inputs=refresh_inputs,
            outputs=nav_outputs,
        )
        calendar_today_button.click(
            _today_month,
            inputs=[workspace_name, calendar_status_filter, calendar_type_filter],
            outputs=nav_outputs,
        )

        calendar_status_filter.change(
            refresh_content_calendar,
            inputs=refresh_inputs,
            outputs=[calendar_output, upcoming_output],
        )
        calendar_type_filter.change(
            refresh_content_calendar,
            inputs=refresh_inputs,
            outputs=[calendar_output, upcoming_output],
        )

        calendar_add_button.click(
            add_content_item,
            inputs=[
                calendar_title,
                calendar_content_type,
                calendar_game_topic,
                calendar_status,
                calendar_publish_date,
                calendar_notes,
                workspace_name,
                calendar_month,
                calendar_year,
                calendar_status_filter,
                calendar_type_filter,
            ],
            outputs=[
                calendar_output,
                upcoming_output,
                calendar_item_picker,
                calendar_message,
            ],
        )

        calendar_load_button.click(
            load_selected_content_item,
            inputs=[calendar_item_picker, workspace_name],
            outputs=[
                calendar_title,
                calendar_content_type,
                calendar_game_topic,
                calendar_status,
                calendar_publish_date,
                calendar_notes,
                calendar_message,
            ],
        )

        calendar_update_button.click(
            update_content_item,
            inputs=[
                calendar_item_picker,
                calendar_title,
                calendar_content_type,
                calendar_game_topic,
                calendar_status,
                calendar_publish_date,
                calendar_notes,
                workspace_name,
                calendar_month,
                calendar_year,
                calendar_status_filter,
                calendar_type_filter,
            ],
            outputs=[
                calendar_output,
                upcoming_output,
                calendar_item_picker,
                calendar_message,
            ],
        )

        calendar_delete_button.click(
            delete_content_item,
            inputs=[
                calendar_item_picker,
                workspace_name,
                calendar_month,
                calendar_year,
                calendar_status_filter,
                calendar_type_filter,
            ],
            outputs=[
                calendar_output,
                upcoming_output,
                calendar_item_picker,
                calendar_message,
            ],
        )

        plan_week_button.click(
            plan_my_week,
            inputs=[workspace_name],
            outputs=plan_week_output,
            show_progress="full",
        )

    return calendar_page, calendar_output, upcoming_output, calendar_item_picker


# Temporary compatibility alias.
build_calendar_tab = build_calendar_page


      
