# Channel Coach - Content Calendar UI

import gradio as gr
from datetime import date

from features import (
    CONTENT_TYPES,
    CONTENT_STATUSES,
    render_content_calendar,
    render_upcoming_content,
    get_calendar_choices,
    add_content_item,
    refresh_content_calendar,
    load_selected_content_item,
    update_content_item,
    delete_content_item,
    plan_my_week,
)

def build_calendar_tab(workspace_name):
    """Build the Content Calendar tab."""

    with gr.Tab("📅 Content Calendar"):
        gr.Markdown(
            """
            ## 📅 Content Calendar
            Plan your long videos, Shorts, Reels, TikToks, livestreams, and community posts.

            Date format: **YYYY-MM-DD**. Example: **2026-06-28**
            """
        )

        with gr.Row():
            with gr.Column(scale=1):
                calendar_title = gr.Textbox(
                    label="Title",
                    placeholder="Example: Getting the Ice Rod"
                )

                calendar_content_type = gr.Dropdown(
                    CONTENT_TYPES,
                    value="Long Video",
                    label="Content Type"
                )

                calendar_game_topic = gr.Textbox(
                    label="Game / Topic",
                    placeholder="Example: Zelda ALTTP"
                )

                calendar_status = gr.Dropdown(
                    CONTENT_STATUSES,
                    value="Idea",
                    label="Status"
                )

                calendar_publish_date = gr.Textbox(
                    label="Target Publish Date",
                    value=date.today().isoformat(),
                    placeholder="YYYY-MM-DD"
                )

                calendar_notes = gr.Textbox(
                    label="Notes",
                    lines=4,
                    placeholder="Example: Need thumbnail, voiceover, and final export."
                )

                calendar_add_button = gr.Button("➕ Add to Calendar")
                calendar_message = gr.Textbox(
                    label="Calendar Status",
                    lines=2
                )

                upcoming_output = gr.HTML(
                    value=render_upcoming_content(user_id="main")
                )

                plan_week_button = gr.Button("✨ Plan My Week")
                plan_week_output = gr.Textbox(
                    label="Weekly Content Plan",
                    lines=12
                )

            with gr.Column(scale=2):
                with gr.Row():
                    calendar_month = gr.Dropdown(
                        choices=list(range(1, 13)),
                        value=date.today().month,
                        label="Month"
                    )

                    calendar_year = gr.Number(
                        value=date.today().year,
                        label="Year",
                        precision=0
                    )

                with gr.Row():
                    calendar_status_filter = gr.Dropdown(
                        ["All"] + CONTENT_STATUSES,
                        value="All",
                        label="Status Filter"
                    )

                    calendar_type_filter = gr.Dropdown(
                        ["All"] + CONTENT_TYPES,
                        value="All",
                        label="Type Filter"
                    )

                calendar_output = gr.HTML(
                    value=render_content_calendar(user_id="main")
                )

                calendar_refresh_button = gr.Button(
                    "🔄 Refresh Calendar"
                )

        gr.Markdown("### Edit or Delete Calendar Item")

        calendar_item_picker = gr.Dropdown(
            choices=get_calendar_choices("main"),
            label="Choose Calendar Item"
        )

        calendar_load_button = gr.Button("📂 Load Selected Item")

        with gr.Row():
            calendar_update_button = gr.Button("💾 Save Edit")
            calendar_delete_button = gr.Button(
                "🗑️ Delete Selected Item"
            )
