# Channel Coach - Content Calendar UI

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


def build_calendar_page(workspace_name, visible=False):
    """
    Build the Content Calendar page and wire all Calendar events.

    Returns:
        calendar_page
        calendar_output
        upcoming_output
        calendar_item_picker

    app.py uses those returned components for navigation and workspace refreshes.
    """

    with gr.Column(
        visible=visible,
        elem_id="calendar-page",
    ) as calendar_page:

        gr.HTML(
            """
            <style>
              #calendar-page {
                  max-width: 1200px;
                  margin: 0 auto;
              }

              #calendar-page .cc-calendar-title {
                  margin-bottom: 2px;
              }

              #calendar-page .cc-calendar-subtitle {
                  opacity: .72;
                  margin-bottom: 18px;
              }

              #calendar-page .cc-card {
                  border: 1px solid rgba(255,62,165,.32);
                  border-radius: 16px;
                  padding: 18px;
                  background: rgba(7,10,17,.88);
              }

              #calendar-page .cc-toolbar {
                  border: 1px solid rgba(255,62,165,.32);
                  border-radius: 16px;
                  padding: 18px;
                  margin-bottom: 14px;
                  background: rgba(7,10,17,.88);
              }

              #calendar-page .cc-calendar-main {
                  min-height: 520px;
              }
            </style>

            <div class="cc-calendar-title">
                <h2>📅 Content Calendar</h2>
            </div>

            <div class="cc-calendar-subtitle">
                Plan long videos, Shorts, Reels, TikToks,
                livestreams, and community posts.
            </div>
            """
        )

        # =====================================================
        # ADD CONTENT + SCHEDULE
        # =====================================================
        with gr.Row(equal_height=False):

            # -------------------------
            # ADD CONTENT
            # -------------------------
            with gr.Column(
                scale=1,
                min_width=300,
                elem_classes=["cc-card"],
            ):
                gr.Markdown("### ➕ Add Content")

                gr.HTML('<div class="cc-field-label">Title</div>')
                calendar_title = gr.Textbox(
                    show_label=False,
                    placeholder="Example: Getting the Ice Rod",
                    elem_classes=["cc-cyber-field"],
                )

                gr.HTML('<div class="cc-field-label">Content Type</div>')
                calendar_content_type = gr.Dropdown(
                    CONTENT_TYPES,
                    value="Long Video",
                    show_label=False,
                    elem_classes=["cc-cyber-field"],
                )

                gr.HTML('<div class="cc-field-label">Game / Topic</div>')
                calendar_game_topic = gr.Textbox(
                    show_label=False,
                    placeholder="Example: Zelda ALTTP",
                    elem_classes=["cc-cyber-field"],
                )

                gr.HTML('<div class="cc-field-label">Status</div>')
                calendar_status = gr.Dropdown(
                    CONTENT_STATUSES,
                    value="Idea",
                    show_label=False,
                    elem_classes=["cc-cyber-field"],
                )

                gr.HTML('<div class="cc-field-label">Target Publish Date</div>')
                calendar_publish_date = gr.Textbox(
                    show_label=False,
                    value=date.today().isoformat(),
                    placeholder="YYYY-MM-DD",
                    elem_classes=["cc-cyber-field"],
                )

                gr.HTML('<div class="cc-field-label">Notes</div>')
                calendar_notes = gr.Textbox(
                    show_label=False,
                    lines=4,
                    placeholder=(
                        "Example: Need thumbnail, voiceover, "
                        "and final export."
                    ),
                    elem_classes=["cc-cyber-field"],
                )

                calendar_add_button = gr.Button(
                    "➕ Add to Calendar"
                )

                calendar_message = gr.Textbox(
                    show_label=False,
                    placeholder="Calendar status",
                    lines=2,
                    elem_classes=["cc-cyber-field"],
                )

                upcoming_output = gr.HTML(
                    value=render_upcoming_content(user_id="main")
                )

                plan_week_button = gr.Button(
                    "✨ Plan My Week"
                )

                plan_week_output = gr.Textbox(
                    show_label=False,
                    placeholder="Weekly content plan",
                    lines=12,
                    elem_classes=["cc-cyber-field"],
                )

            # -------------------------
            # SCHEDULE
            # -------------------------
            with gr.Column(
                scale=2,
                min_width=520,
            ):
                gr.Markdown("### 🗓️ Schedule")

                with gr.Row(
                    elem_classes=["cc-toolbar"]
                ):
                    with gr.Column():
                        gr.HTML(
                            '<div class="cc-field-label">Month</div>'
                        )
                        calendar_month = gr.Dropdown(
                            choices=list(range(1, 13)),
                            value=date.today().month,
                            show_label=False,
                            elem_classes=["cc-cyber-field"],
                        )

                    with gr.Column():
                        gr.HTML(
                            '<div class="cc-field-label">Year</div>'
                        )
                        calendar_year = gr.Number(
                            value=date.today().year,
                            show_label=False,
                            precision=0,
                            elem_classes=["cc-cyber-field"],
                        )

                    with gr.Column():
                        gr.HTML(
                            '<div class="cc-field-label">Status Filter</div>'
                        )
                        calendar_status_filter = gr.Dropdown(
                            ["All"] + CONTENT_STATUSES,
                            value="All",
                            show_label=False,
                            elem_classes=["cc-cyber-field"],
                        )

                    with gr.Column():
                        gr.HTML(
                            '<div class="cc-field-label">Type Filter</div>'
                        )
                        calendar_type_filter = gr.Dropdown(
                            ["All"] + CONTENT_TYPES,
                            value="All",
                            show_label=False,
                            elem_classes=["cc-cyber-field"],
                        )

                with gr.Column(
                    elem_classes=[
                        "cc-card",
                        "cc-calendar-main",
                    ]
                ):
                    calendar_output = gr.HTML(
                        value=render_content_calendar(
                            user_id="main"
                        )
                    )

                calendar_refresh_button = gr.Button(
                    "🔄 Refresh Calendar"
                )

        # =====================================================
        # EDIT / DELETE CONTENT
        # =====================================================
        gr.Markdown("### ✏️ Edit or Delete Content")

        with gr.Column(
            elem_classes=["cc-card"]
        ):
            gr.HTML(
                '<div class="cc-field-label">'
                'Choose Calendar Item'
                '</div>'
            )

            calendar_item_picker = gr.Dropdown(
                choices=get_calendar_choices("main"),
                show_label=False,
                elem_classes=["cc-cyber-field"],
            )

            calendar_load_button = gr.Button(
                "📂 Load Selected Item"
            )

            with gr.Row():
                calendar_update_button = gr.Button(
                    "💾 Save Edit"
                )
                calendar_delete_button = gr.Button(
                    "🗑️ Delete Selected Item"
                )

        # =====================================================
        # EVENT WIRING
        # =====================================================
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

        refresh_inputs = [
            workspace_name,
            calendar_month,
            calendar_year,
            calendar_status_filter,
            calendar_type_filter,
        ]

        calendar_refresh_button.click(
            refresh_content_calendar,
            inputs=refresh_inputs,
            outputs=[
                calendar_output,
                upcoming_output,
            ],
        )

        calendar_month.change(
            refresh_content_calendar,
            inputs=refresh_inputs,
            outputs=[
                calendar_output,
                upcoming_output,
            ],
        )

        calendar_year.change(
            refresh_content_calendar,
            inputs=refresh_inputs,
            outputs=[
                calendar_output,
                upcoming_output,
            ],
        )

        calendar_status_filter.change(
            refresh_content_calendar,
            inputs=refresh_inputs,
            outputs=[
                calendar_output,
                upcoming_output,
            ],
        )

        calendar_type_filter.change(
            refresh_content_calendar,
            inputs=refresh_inputs,
            outputs=[
                calendar_output,
                upcoming_output,
            ],
        )

        calendar_load_button.click(
            load_selected_content_item,
            inputs=[
                calendar_item_picker,
                workspace_name,
            ],
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

    return (
        calendar_page,
        calendar_output,
        upcoming_output,
        calendar_item_picker,
    )


# Temporary compatibility alias.
# Anything still importing build_calendar_tab will continue working
# while we finish organizing the rest of the app.
build_calendar_tab = build_calendar_page

      
