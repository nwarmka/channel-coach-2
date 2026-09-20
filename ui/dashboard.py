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
        dashboard_page
        dashboard_output
        dashboard_open_calendar_button

    The calendar button is kept as a hidden Gradio bridge because app.py
    expects it, but it is no longer shown on the Home screen.
    """

    css = """
    /* =========================================================
       MAIN DASHBOARD PAGE
       ========================================================= */

    #dashboard-page {
        padding-top: 0 !important;
        width: 100% !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        background: transparent !important;
    }

    /* =========================================================
       CREATOR DASHBOARD HEADER
       Keep this rounded.
       ========================================================= */

    #dashboard-page .cc-dashboard-page-header {
        width: 100%;
        margin: 0 0 14px 0;
        padding: 18px 22px;
        border: 2px solid rgba(190, 35, 143, .88);
        border-radius: 20px;
        background: linear-gradient(
            180deg,
            rgba(10, 14, 25, .98),
            rgba(5, 8, 15, .99)
        );
        box-sizing: border-box;
        box-shadow: 0 0 24px rgba(255, 62, 165, .08);
    }

    #dashboard-page .cc-dashboard-page-title {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 0;
        color: #ff3ea5;
        font-size: 1.75rem;
        font-weight: 900;
        line-height: 1.1;
    }

    #dashboard-page .cc-dashboard-page-subtitle {
        margin-top: 8px;
        color: #9aa7bd;
        font-size: .98rem;
        line-height: 1.4;
    }

    /* =========================================================
       REMOVE RECTANGULAR / 90-DEGREE OUTER WRAPPERS
       ========================================================= */

    #dashboard-output {
        margin-top: 0 !important;
        width: 100% !important;
        padding: 0 !important;

        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        background: transparent !important;
    }

    #dashboard-output > div,
    #dashboard-output > div > div,
    #dashboard-output .cc-dashboard-wrap,
    #dashboard-output .cc-dashboard-hero,
    #dashboard-output .cc-upcoming-box {
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        background: transparent !important;
    }

    /*
       Remove Gradio component shells that can create
       square/rectangular borders around the dashboard.
    */
    #dashboard-page .gradio-container,
    #dashboard-page .block,
    #dashboard-page .form,
    #dashboard-page .wrap,
    #dashboard-output.block,
    #dashboard-output .block {
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
    }

    /*
       Do not allow Gradio's outer HTML component to create
       its own rectangular card/background.
    */
    #dashboard-output,
    #dashboard-output.block,
    #dashboard-output.form {
        border: 0 !important;
        outline: 0 !important;
        box-shadow: none !important;
        background: transparent !important;
    }

    /* Main dashboard content wrapper */
    #dashboard-output .cc-dashboard-wrap {
        width: 100% !important;
        padding: 0 !important;
        gap: 14px !important;
    }

    /* =========================================================
       DASHBOARD HERO CONTENT
       No outer rectangular card.
       ========================================================= */

    #dashboard-output .cc-dashboard-hero {
        padding: 15px 18px !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        background: transparent !important;
    }

    #dashboard-output .cc-dashboard-hero h2 {
        margin: .15rem 0 .12rem !important;
        font-size: 1.45rem !important;
    }

    #dashboard-output .cc-dashboard-hero p {
        margin: 0 !important;
        font-size: .86rem !important;
    }

    #dashboard-output .cc-small-label {
        font-size: .68rem !important;
        letter-spacing: .11em !important;
    }

    /* =========================================================
       NEXT CREATOR TASKS
       ========================================================= */

    #dashboard-output .cc-upcoming-box {
        width: 100% !important;
        box-sizing: border-box !important;
        padding: 4px 0 0 !important;
        margin: 0 !important;

        background: transparent !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
    }

    #dashboard-output .cc-upcoming-box h3 {
        margin: 0 0 4px !important;
        color: #f7f7fb !important;
        font-size: 1.45rem !important;
        font-weight: 900 !important;
        line-height: 1.15 !important;
    }

    #dashboard-output .cc-upcoming-box > .cc-empty {
        margin: 0 0 14px !important;
        color: #93a0b6 !important;
        font-size: .9rem !important;
    }

    /* =========================================================
       CLICKABLE TASK LINKS
       ========================================================= */

    #dashboard-output a.cc-dashboard-task-link {
        display: block !important;
        width: 100% !important;
        margin: 0 0 10px !important;
        text-decoration: none !important;
        color: inherit !important;

        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        background: transparent !important;
    }

    /* =========================================================
       INDIVIDUAL TASK CARDS
       KEEP THESE ROUNDED BORDERS.
       ========================================================= */

    #dashboard-output .cc-planner-project-card {
        position: relative !important;
        width: 100% !important;
        min-height: 82px !important;
        box-sizing: border-box !important;

        margin: 0 !important;
        padding: 15px 54px 15px 18px !important;

        border: 2px solid #253044 !important;
        border-radius: 16px !important;
```
