import gradio as gr

from features import (
    dashboard_ai_tip,
    refresh_creator_dashboard,
    render_creator_dashboard,
)


def build_dashboard_page(workspace_name, visible=True):
    """
    Build the Creator Dashboard page.

    Returns:
        dashboard_page: the page container used by app.py navigation
        dashboard_output: the main dashboard HTML component used by workspace refreshes
    """
    with gr.Column(
        visible=visible,
        elem_id="dashboard-page",
    ) as dashboard_page:
        gr.Markdown(
            "## 🕹️ Creator Dashboard\n\n"
            "Your home base for upcoming content, overdue projects, "
            "and quick creator guidance."
        )

        dashboard_output = gr.HTML(
            value=render_creator_dashboard("main")
        )

        with gr.Row():
            dashboard_refresh_button = gr.Button(
                "🔄 Refresh Dashboard"
            )
            dashboard_tip_button = gr.Button(
                "✨ Give Me One Tip"
            )

        dashboard_tip_output = gr.Textbox(
            label="Creator Tip",
            lines=5,
        )

        dashboard_refresh_button.click(
            refresh_creator_dashboard,
            inputs=[workspace_name],
            outputs=dashboard_output,
        )

        dashboard_tip_button.click(
            dashboard_ai_tip,
            inputs=[workspace_name],
            outputs=dashboard_tip_output,
            show_progress="full",
        )

    return dashboard_page, dashboard_output

