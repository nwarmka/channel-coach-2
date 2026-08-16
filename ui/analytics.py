# Channel Coach - Analytics UI

import gradio as gr

from features import (
    render_analytics_tracker,
    save_analytics_snapshot,
)


def build_analytics_page(workspace_name, visible=False):
    """Build the Analytics Tracker page and wire its events."""

    with gr.Column(
        visible=visible,
        elem_id="analytics-page",
    ) as analytics_page:

        gr.Markdown(
            """
            ## 📊 Analytics Tracker
            Manually save your YouTube stats so Channel Coach can
            track growth over time.
            """
        )

        analytics_output = gr.HTML(
            value=render_analytics_tracker("main")
        )

        with gr.Accordion(
            "➕ Add Analytics Snapshot",
            open=True,
        ):
            with gr.Row():
                analytics_views = gr.Number(
                    label="Total Views",
                    value=0,
                    precision=0,
                )

                analytics_subscribers = gr.Number(
                    label="Subscribers",
                    value=0,
                    precision=0,
                )

            with gr.Row():
                analytics_watch_time = gr.Number(
                    label="Watch Time Hours",
                    value=0,
                )

                analytics_ctr = gr.Number(
                    label="CTR %",
                    value=0,
                )

            analytics_notes = gr.Textbox(
                label="Notes",
                placeholder=(
                    "Example: Posted 3 Shorts this week, Zelda guide "
                    "performed well, took a 2-week break..."
                ),
                lines=3,
            )

            analytics_save_button = gr.Button(
                "💾 Save Analytics Snapshot"
            )

            analytics_status = gr.Markdown()

            analytics_save_button.click(
                save_analytics_snapshot,
                inputs=[
                    analytics_views,
                    analytics_subscribers,
                    analytics_watch_time,
                    analytics_ctr,
                    analytics_notes,
                    workspace_name,
                ],
                outputs=[
                    analytics_status,
                    analytics_output,
                ],
            )

        analytics_refresh_button = gr.Button(
            "🔄 Refresh Analytics"
        )

        analytics_refresh_button.click(
            render_analytics_tracker,
            inputs=[workspace_name],
            outputs=analytics_output,
        )

    return analytics_page, analytics_output

