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
    #dashboard-page {
        padding-top: 0 !important;
        width: 100% !important;
    }

    #dashboard-page .cc-dashboard-page-header {
        width: 100%;
        margin: 0 0 14px 0;
        padding: 18px 22px;
        border: 2px solid rgba(190, 35, 143, .88);
        border-radius: 20px;
        background: linear-gradient(180deg, rgba(10, 14, 25, .98), rgba(5, 8, 15, .99));
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

    #dashboard-output {
        margin-top: 0 !important;
        width: 100% !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        background: transparent !important;
        padding: 0 !important;
    }

    /* Remove the large outer Creator Dashboard wrapper/card.
       Individual task cards keep their own borders. */
    #dashboard-output .cc-dashboard-wrap {
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        background: transparent !important;
        padding: 0 !important;
    }

    #dashboard-output .cc-dashboard-wrap {
        gap: 14px !important;
        width: 100% !important;
    }

    /* Keep the existing dashboard data, but make the task area the visual focus. */
    #dashboard-output .cc-dashboard-hero {
        padding: 15px 18px !important;
        border-radius: 16px !important;
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

    /* NEXT CREATOR TASKS PANEL */
    #dashboard-output .cc-upcoming-box {
        width: 100% !important;
        box-sizing: border-box !important;
        padding: 4px 0 0 !important;
        margin: 0 !important;
        background: transparent !important;
        border: 0 !important;
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

    /* Clickable task rows */
    #dashboard-output a.cc-dashboard-task-link {
        display: block !important;
        width: 100% !important;
        margin: 0 0 10px !important;
        text-decoration: none !important;
        color: inherit !important;
    }

    #dashboard-output .cc-planner-project-card {
        position: relative !important;
        width: 100% !important;
        min-height: 82px !important;
        box-sizing: border-box !important;
        margin: 0 !important;
        padding: 15px 54px 15px 18px !important;
        border: 2px solid #253044 !important;
        border-radius: 16px !important;
        background: linear-gradient(180deg, #0b101a, #070b13) !important;
        box-shadow: none !important;
        transition: border-color .16s ease, transform .16s ease, box-shadow .16s ease !important;
    }

    #dashboard-output a.cc-dashboard-task-link:hover .cc-planner-project-card {
        transform: translateY(-1px) !important;
        border-color: rgba(255, 62, 165, .72) !important;
        box-shadow: 0 0 20px rgba(255, 62, 165, .09) !important;
    }

    #dashboard-output .cc-planner-project-card::after {
        content: "›";
        position: absolute;
        right: 19px;
        top: 50%;
        transform: translateY(-54%);
        color: #ff3ea5;
        font-size: 2.15rem;
        font-weight: 300;
        line-height: 1;
    }

    #dashboard-output .cc-planner-card-top {
        display: grid !important;
        grid-template-columns: minmax(0, 1fr) auto !important;
        align-items: center !important;
        gap: 16px !important;
        width: 100% !important;
    }

    #dashboard-output .cc-planner-title {
        color: #f8f9fc !important;
        font-size: 1rem !important;
        font-weight: 850 !important;
        line-height: 1.25 !important;
    }

    #dashboard-output .cc-planner-meta {
        margin-top: 5px !important;
        color: #8fa0b8 !important;
        font-size: .8rem !important;
        line-height: 1.3 !important;
    }

    #dashboard-output .cc-planner-topic {
        display: none !important;
    }

    #dashboard-output .cc-planner-pill {
        min-width: 48px !important;
        padding: 0 !important;
        border: 0 !important;
        background: transparent !important;
        color: #a9bce0 !important;
        font-size: 1.05rem !important;
        font-weight: 850 !important;
        text-align: right !important;
        box-shadow: none !important;
    }

    /* Restore the visible task progress bar. */
    #dashboard-output .cc-progress-wrap {
        display: block !important;
        width: 100% !important;
        height: 10px !important;
        margin-top: 12px !important;
        overflow: hidden !important;
        border: 0 !important;
        border-radius: 999px !important;
        background: #263246 !important;
        box-shadow: inset 0 1px 2px rgba(0,0,0,.45) !important;
    }

    #dashboard-output .cc-progress-fill {
        display: block !important;
        height: 100% !important;
        min-width: 0 !important;
        border-radius: 999px !important;
        background: linear-gradient(90deg, #ff1493, #ff4fb8) !important;
        box-shadow: 0 0 10px rgba(255, 20, 147, .24) !important;
    }

    /* Remove the big native calendar button from Home.
       It remains rendered off-screen so app.py's existing event wiring is safe. */
    #dashboard-open-calendar {
        position: fixed !important;
        left: -10000px !important;
        top: -10000px !important;
        width: 1px !important;
        height: 1px !important;
        min-height: 0 !important;
        overflow: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
        margin: 0 !important;
        padding: 0 !important;
        border: 0 !important;
    }

    #dashboard-actions {
        width: min(620px, 100%) !important;
        margin: 8px 0 0 !important;
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
            padding: 14px 15px;
            margin-bottom: 10px;
        }

        #dashboard-page .cc-dashboard-page-title {
            font-size: 1.28rem;
        }

        #dashboard-page .cc-dashboard-page-subtitle {
            font-size: .82rem;
        }

        #dashboard-output .cc-planner-project-card {
            min-height: 76px !important;
            padding: 13px 42px 13px 14px !important;
        }

        #dashboard-output .cc-planner-title {
            font-size: .92rem !important;
        }

        #dashboard-output .cc-planner-meta {
            font-size: .72rem !important;
        }

        #dashboard-output .cc-planner-pill {
            font-size: .92rem !important;
            min-width: 42px !important;
        }

        #dashboard-output .cc-progress-wrap {
            height: 8px !important;
            margin-top: 10px !important;
        }

        #dashboard-output .cc-planner-project-card::after {
            right: 13px;
            font-size: 1.8rem;
        }
    }
    """

    with gr.Column(visible=visible, elem_id="dashboard-page") as dashboard_page:
        gr.HTML(
            f"<style>#dashboard-style {{ display: none !important; }}\n{css}</style>",
            elem_id="dashboard-style",
        )

        gr.HTML(
            """
            <div class="cc-dashboard-page-header">
                <div class="cc-dashboard-page-title">
                    <span>🎮</span>
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
            js_on_load=r"""
                // Event delegation means refreshed dashboard HTML keeps working.
                element.addEventListener("click", (event) => {
                    const card = event.target.closest("a.cc-dashboard-task-link");
                    if (!card || !element.contains(card)) return;

                    const dateValue = card.dataset.date || "";
                    if (!dateValue) return;

                    event.preventDefault();
                    event.stopPropagation();

                    trigger("submit", {date: dateValue});
                });
            """,
        )

        # app.py expects this component, so keep it as the existing bridge.
        # CSS above hides it from the Home screen.
        dashboard_open_calendar_button = gr.Button(
            "📅 Open Next Creator Task in Calendar",
            elem_id="dashboard-open-calendar",
            variant="primary",
        )

        with gr.Row(elem_id="dashboard-actions"):
            dashboard_refresh_button = gr.Button("🔄 Refresh Dashboard")
            dashboard_tip_button = gr.Button("✨ Give Me One Tip")

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

    return dashboard_page, dashboard_output, dashboard_open_calendar_button








    
 
        
 
      
 
      
    
 
      
    
 
      


    
 
      
 
      
    
 
      
      
    
 
      
    
 
      













    
 
        
 
      
 
      
    
 
      
    
 
      


    
 
      
 
      
    
 
      
      
    
 
      
    
 
      
