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

    css = """
    #dashboard-page {
        padding-top: 0 !important;
    }

    /* Compact page title area */
    #dashboard-page .cc-dashboard-page-header {
        width: 100%;
        margin: 0 0 10px 0;
        padding: 10px 14px;
        border: 1px solid rgba(168, 85, 247, .34);
        border-radius: 16px;
        background: rgba(10, 13, 25, .78);
        box-sizing: border-box;
    }

    #dashboard-page .cc-dashboard-page-title {
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 0;
        color: #ff4db8;
        font-size: 1.25rem;
        font-weight: 850;
        letter-spacing: -.01em;
        line-height: 1.1;
    }

    #dashboard-page .cc-dashboard-page-subtitle {
        margin-top: 5px;
        color: rgba(226, 232, 240, .74);
        font-size: .88rem;
        line-height: 1.35;
    }

    /* Tighten the rendered dashboard area */
    #dashboard-output {
        margin-top: 0 !important;
    }

    #dashboard-output .cc-dashboard-wrap {
        gap: 10px !important;
    }

    /* Make the Welcome Back card much more compact */
    #dashboard-output .cc-dashboard-hero {
        padding: 14px 18px !important;
        border-radius: 16px !important;
        min-height: 0 !important;
    }

    #dashboard-output .cc-dashboard-hero h2 {
        margin: .15rem 0 .12rem !important;
        font-size: 1.55rem !important;
        line-height: 1.08 !important;
    }

    #dashboard-output .cc-dashboard-hero p {
        margin: 0 !important;
        font-size: .86rem !important;
        line-height: 1.3 !important;
    }

    #dashboard-output .cc-small-label {
        font-size: .66rem !important;
        letter-spacing: .11em !important;
        line-height: 1.1 !important;
    }

    /* Keep dashboard controls compact and visually secondary */
    #dashboard-actions {
        width: min(620px, 100%) !important;
        margin: 6px 0 0 !important;
        gap: 8px !important;
    }

    #dashboard-actions button {
        min-height: 38px !important;
        padding-top: 6px !important;
        padding-bottom: 6px !important;
        border-radius: 12px !important;
    }

    #dashboard-tip-output {
        margin-top: 6px !important;
    }

    @media (max-width: 700px) {
        #dashboard-page .cc-dashboard-page-header {
            padding: 9px 11px;
            margin-bottom: 8px;
        }

        #dashboard-page .cc-dashboard-page-title {
            font-size: 1.08rem;
        }

        #dashboard-page .cc-dashboard-page-subtitle {
            font-size: .80rem;
        }

        #dashboard-output .cc-dashboard-hero {
            padding: 12px 14px !important;
        }

        #dashboard-output .cc-dashboard-hero h2 {
            font-size: 1.35rem !important;
        }
    }
    """

    with gr.Column(
        visible=visible,
        elem_id="dashboard-page",
    ) as dashboard_page:
        gr.HTML(f"<style>{css}</style>")

        gr.HTML(
            """
            <div class="cc-dashboard-page-header">
                <div class="cc-dashboard-page-title">
                    <span>🕹️</span>
                    <span>Creator Dashboard</span>
                </div>
                <div class="cc-dashboard-page-subtitle">
                    Your home base for upcoming content, overdue projects, and quick creator guidance.
                </div>
            </div>
            """
        )

        dashboard_output = gr.HTML(
            value=render_creator_dashboard("main"),
            elem_id="dashboard-output",
        )

        with gr.Row(elem_id="dashboard-actions"):
            dashboard_refresh_button = gr.Button(
                "🔄 Refresh Dashboard"
            )
            dashboard_tip_button = gr.Button(
                "✨ Give Me One Tip"
            )

        dashboard_tip_output = gr.Textbox(
            label="Creator Tip",
            lines=5,
            elem_id="dashboard-tip-output",
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

