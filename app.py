# Channel Coach main app
# UI lives here. Feature functions, styles, constants, and helpers are imported from features.py.

from features import *
from ui.calendar import build_calendar_tab


with gr.Blocks(title="Channel Coach", head=custom_head, css=custom_css) as app:

    gr.HTML("""
    <style>
    :root{
      --bg:#05070d; --panel:#0b0f19; --panel2:#101521; --line:#273047;
      --text:#f7f7fb; --muted:#9aa5bd; --pink:#ff3ea5; --hot:#ff4fd8;
      --purple:#8b5cf6; --blue:#2f7cff; --cyan:#16d9ff;
    }

    html,body,.gradio-container{
      background:
        radial-gradient(circle at 12% 5%,rgba(139,92,246,.16),transparent 28%),
        radial-gradient(circle at 88% 8%,rgba(22,217,255,.10),transparent 25%),
        linear-gradient(180deg,#03050a,#070a12)!important;
      color:var(--text)!important;
      min-height:100%;
    }

    .gradio-container{max-width:100%!important;padding:0!important}
    #channel-coach-app{max-width:1480px!important;margin:0 auto!important;padding:20px 24px 36px!important}

    h1,h2,h3,h4,h5,h6,.prose h1,.prose h2,.prose h3{color:var(--text)!important}
    p,.prose p,.prose li,label,.label-wrap span{color:var(--muted)!important}

    #channel-coach-app .gr-box,
    #channel-coach-app .block,
    #channel-coach-app .panel,
    #channel-coach-app .form,
    #channel-coach-app .cc-card,
    #channel-coach-app .cc-toolbar{
      background:linear-gradient(180deg,rgba(13,17,29,.97),rgba(7,10,18,.99))!important;
      border:1px solid rgba(139,92,246,.34)!important;
      border-radius:18px!important;
      box-shadow:0 16px 34px rgba(0,0,0,.34),0 0 28px rgba(139,92,246,.05)!important;
    }

    #channel-coach-app input,
    #channel-coach-app textarea,
    #channel-coach-app select,
    #channel-coach-app [role="combobox"]{
      background:#070a11!important;
      color:#fff!important;
      border:1px solid #303a50!important;
      border-radius:12px!important;
      box-shadow:none!important;
    }

    #channel-coach-app input:focus,
    #channel-coach-app textarea:focus,
    #channel-coach-app [role="combobox"]:focus{
      border-color:var(--cyan)!important;
      box-shadow:0 0 0 2px rgba(22,217,255,.12),0 0 18px rgba(22,217,255,.10)!important;
    }

    #channel-coach-app input::placeholder,
    #channel-coach-app textarea::placeholder{color:#667089!important}

    #channel-coach-app button{
      background:linear-gradient(180deg,#111622,#0a0e17)!important;
      color:#fff!important;
      border:1px solid rgba(47,124,255,.60)!important;
      border-radius:12px!important;
      font-weight:700!important;
      box-shadow:0 0 18px rgba(47,124,255,.07)!important;
      transition:.18s ease!important;
    }

    #channel-coach-app button:hover{
      transform:translateY(-1px);
      border-color:var(--pink)!important;
      box-shadow:0 0 22px rgba(255,62,165,.20)!important;
    }

    #channel-coach-app button.primary{
      background:linear-gradient(90deg,var(--purple),var(--pink))!important;
      border-color:transparent!important;
      box-shadow:0 0 28px rgba(255,62,165,.22)!important;
    }

    #channel-coach-menu{
      width:280px!important; max-width:280px!important;
      position:fixed!important; left:22px!important; top:82px!important; z-index:9999!important;
      padding:14px!important;
      background:rgba(5,7,13,.98)!important;
      border:1px solid rgba(139,92,246,.56)!important;
      border-radius:18px!important;
      box-shadow:0 20px 50px rgba(0,0,0,.58),0 0 30px rgba(139,92,246,.14)!important;
      backdrop-filter:blur(18px);
    }

    #channel-coach-menu button{
      width:100%!important; justify-content:flex-start!important; margin:4px 0!important;
      border-color:transparent!important; background:transparent!important; color:#eef1f8!important;
    }

    #channel-coach-menu button:hover{
      background:linear-gradient(90deg,rgba(139,92,246,.20),rgba(255,62,165,.15))!important;
      border-color:rgba(255,62,165,.42)!important;
    }

    #chat-page{
      max-width:980px!important; margin:20px auto 0!important; padding:28px!important;
      border:1px solid rgba(22,217,255,.28)!important; border-radius:22px!important;
      background:linear-gradient(180deg,rgba(12,16,27,.98),rgba(6,9,16,.99))!important;
      box-shadow:0 22px 60px rgba(0,0,0,.38),0 0 34px rgba(22,217,255,.07)!important;
    }

    #chat-page h2{color:var(--cyan)!important;text-transform:uppercase;letter-spacing:.05em}

    #calendar-page,#dashboard-page,#projects-page,#toolkit-page,#analytics-page,#settings-page{
      max-width:1400px!important;margin:0 auto!important;
    }

    #calendar-page h2,#dashboard-page h2,#projects-page h2,#toolkit-page h2,#analytics-page h2,#settings-page h2{
      background:linear-gradient(90deg,var(--pink),var(--purple),var(--cyan));
      -webkit-background-clip:text;background-clip:text;color:transparent!important;
    }

    #calendar-page .cc-card,#calendar-page .cc-toolbar,#calendar-page .cc-calendar-main{
      background:linear-gradient(180deg,#0b0f18,#070a11)!important;
      border-color:rgba(255,62,165,.32)!important;
    }

    #calendar-page [role="combobox"],#calendar-page .dropdown input{
      background:#06090f!important;color:#fff!important;border-color:#4b255b!important;
    }

    #login-screen{
      max-width:520px!important;margin:7vh auto!important;padding:24px!important;
      background:linear-gradient(180deg,rgba(11,15,25,.98),rgba(5,7,13,.99))!important;
      border:1px solid rgba(139,92,246,.45)!important;border-radius:24px!important;
      box-shadow:0 24px 70px rgba(0,0,0,.58),0 0 40px rgba(255,62,165,.09)!important;
    }

    #login-screen h2{
      background:linear-gradient(90deg,var(--pink),var(--purple),var(--cyan));
      -webkit-background-clip:text;color:transparent!important;
    }

    #login-screen input{
      background:#070a11!important;
      color:#fff!important;
      border:1px solid #343d55!important;
      border-radius:12px!important;
      min-height:48px!important;
    }

    #login-screen input:focus{
      border-color:var(--cyan)!important;
      box-shadow:0 0 0 2px rgba(22,217,255,.10),0 0 20px rgba(22,217,255,.12)!important;
    }

    #login-screen label,
    #login-screen .label-wrap span{
      color:#eef1f8!important;
      font-weight:700!important;
    }

    #login-screen .cc-login-brand{
      text-align:center;
      padding:4px 8px 18px;
    }

    #login-screen .cc-login-logo{
      width:150px;
      max-width:45%;
      height:auto;
      filter:drop-shadow(0 0 20px rgba(255,62,165,.18));
    }

    #login-screen .cc-login-kicker{
      margin-top:12px;
      color:var(--cyan);
      font-size:.78rem;
      letter-spacing:.18em;
      font-weight:800;
    }

    #login-screen .cc-login-brand h1{
      margin:.25rem 0 .4rem!important;
      font-size:2rem!important;
      letter-spacing:.08em;
      background:linear-gradient(90deg,var(--pink),var(--purple),var(--cyan));
      -webkit-background-clip:text;
      background-clip:text;
      color:transparent!important;
    }

    #login-screen .cc-login-brand p{
      margin:0!important;
      color:var(--muted)!important;
    }

    #login-button{
      background:linear-gradient(90deg,var(--purple),var(--pink))!important;
      color:#fff!important;
      border:0!important;
      min-height:48px!important;
      font-weight:900!important;
      letter-spacing:.08em!important;
      box-shadow:0 0 26px rgba(255,62,165,.20)!important;
    }

    #signup-button{
      background:#090d16!important;
      color:var(--cyan)!important;
      border:1px solid rgba(22,217,255,.55)!important;
      min-height:46px!important;
      font-weight:800!important;
      letter-spacing:.05em!important;
    }

    #remember-me{
      background:transparent!important;
      border:0!important;
      box-shadow:none!important;
    }

    #login-status{
      padding:8px 2px 0!important;
    }

    #login-status p{
      color:#dbe2f2!important;
    }

    #workspace-internal{display:none!important}

    *{scrollbar-width:thin;scrollbar-color:#7c3cff #070a10}
    ::-webkit-scrollbar{width:10px;height:10px}
    ::-webkit-scrollbar-track{background:#070a10}
    ::-webkit-scrollbar-thumb{
      background:linear-gradient(var(--purple),var(--pink));
      border-radius:20px;border:2px solid #070a10;
    }

    @media(max-width:900px){
      #channel-coach-app{padding:14px!important}
      #channel-coach-menu{left:12px!important;right:12px!important;width:auto!important;max-width:none!important}
    }
    </style>
    """)

    # =========================
    # ACCOUNT LOGIN
    # =========================
    saved_login = gr.BrowserState(
        empty_saved_session(),
        storage_key="channel_coach_login"
    )

    with gr.Column(visible=True, elem_id="login-screen") as login_screen:
        gr.HTML(
            f"""
            <div class="cc-login-brand">
                <img
                    src="data:image/png;base64,{CHANNEL_COACH_LOGO_BASE64}"
                    alt="Channel Coach Logo"
                    class="cc-login-logo"
                >
                <div class="cc-login-kicker">CREATOR COMMAND CENTER</div>
                <h1>CHANNEL COACH</h1>
                <p>Sign in to enter your creator workspace.</p>
            </div>
            """
        )

        login_email = gr.Textbox(
            label="Email",
            placeholder="you@example.com",
            elem_id="login-email"
        )

        login_password = gr.Textbox(
            label="Password",
            type="password",
            placeholder="Enter your password",
            elem_id="login-password"
        )

        remember_me = gr.Checkbox(
            label="Remember me",
            value=True,
            elem_id="remember-me"
        )

        login_button = gr.Button(
            "LOG IN",
            variant="primary",
            elem_id="login-button"
        )

        signup_button = gr.Button(
            "CREATE ACCOUNT",
            elem_id="signup-button"
        )

        login_status = gr.Markdown(elem_id="login-status")

    with gr.Column(visible=False, elem_id="channel-coach-app") as app_shell:
        # =========================
        # APP SHELL / NAVIGATION
        # =========================
        with gr.Row():
            menu_button = gr.Button("☰", scale=0, min_width=52)
            gr.Markdown("## ✦ CHANNEL COACH")

        with gr.Column(visible=False, elem_id="channel-coach-menu") as menu_panel:
            chat_nav = gr.Button("💬 Coach Chat")
            dashboard_nav = gr.Button("🏠 Dashboard")
            calendar_nav = gr.Button("📅 Calendar")
            projects_nav = gr.Button("📁 Projects")
            toolkit_nav = gr.Button("🎬 Toolkit")
            analytics_nav = gr.Button("📊 Analytics")
            settings_nav = gr.Button("⚙️ Settings")

        menu_open = gr.State(False)

        # The logged-in home screen is Coach Chat.
        with gr.Column(visible=True, elem_id="chat-page") as chat_page:
            gr.Markdown("## 💬 Channel Coach Chat")
            gr.Markdown("Ask Channel Coach what to work on next, what to improve, or how to grow your channel.")
            home_chat_question = gr.Textbox(
                label="Ask Channel Coach",
                placeholder="What should I work on today?",
                lines=3
            )
            home_chat_button = gr.Button("Send", variant="primary")
            home_chat_output = gr.Markdown()

        # =========================
        # WORKSPACE
        # =========================
        # Each tester should use their own workspace name so they do not see another creator's saved data.
        with gr.Column(elem_id="workspace-internal"):
            workspace_name = gr.Textbox(
                label="Workspace Name",
                value="main",
                placeholder="Example: Nikki, Tester1, RetroGamer92",
                info="Use a unique name for your own private Channel Coach workspace."
            )
            workspace_indicator = gr.Markdown("Current workspace: **main**")

            workspace_button = gr.Button("🔄 Load Workspace")

        saved_profile = load_creator_profile("main")

        with gr.Column(visible=False, elem_id="dashboard-page") as dashboard_page:
            gr.Markdown("## 🕹️ Creator Dashboard\n\nYour home base for upcoming content, overdue projects, and quick creator guidance.")
            dashboard_output = gr.HTML(value=render_creator_dashboard("main"))

            with gr.Row():
                dashboard_refresh_button = gr.Button("🔄 Refresh Dashboard")
                dashboard_tip_button = gr.Button("✨ Give Me One Tip")

            dashboard_tip_output = gr.Textbox(label="Creator Tip", lines=5)

            dashboard_refresh_button.click(
                refresh_creator_dashboard,
                inputs=[workspace_name],
                outputs=dashboard_output
            )

            dashboard_tip_button.click(
                dashboard_ai_tip,
                inputs=[workspace_name],
                outputs=dashboard_tip_output,
                show_progress="full"
            )

        def load_workspace_ui(current_workspace):
            safe_workspace = current_workspace or "main"
            profile = load_creator_profile(safe_workspace)
            return (
                f"Current workspace: **{safe_workspace}**",
                render_creator_dashboard(safe_workspace),
                render_content_calendar(user_id=safe_workspace),
                render_upcoming_content(user_id=safe_workspace),
                gr.update(choices=get_calendar_choices(safe_workspace)),
                gr.update(choices=get_calendar_choices(safe_workspace)),
                gr.update(choices=get_calendar_choices(safe_workspace)),
                render_analytics_tracker(safe_workspace),
                render_getting_started_checklist(safe_workspace),
                profile.get("channel_name", ""),
                profile.get("creator_name", ""),
                profile.get("niche", ""),
                profile.get("target_audience", ""),
                profile.get("content_style", ""),
                profile.get("current_games", ""),
                profile.get("main_platforms", ""),
                profile.get("goals", ""),
                profile.get("preferred_tone", ""),
                profile.get("things_to_avoid", "")
            )




        with gr.Column(visible=False, elem_id="calendar-page") as calendar_page:
            gr.HTML("""
            <style>
              #calendar-page {max-width: 1200px; margin: 0 auto;}
              #calendar-page .cc-calendar-title {margin-bottom: 2px;}
              #calendar-page .cc-calendar-subtitle {opacity: .72; margin-bottom: 18px;}
              #calendar-page .cc-card {
                  border: 1px solid rgba(120,120,140,.18);
                  border-radius: 18px;
                  padding: 18px;
                  background: rgba(255,255,255,.72);
                  box-shadow: 0 8px 28px rgba(20,20,40,.06);
              }
              #calendar-page .cc-toolbar {
                  border: 1px solid rgba(120,120,140,.16);
                  border-radius: 16px;
                  padding: 12px;
                  margin-bottom: 14px;
                  background: rgba(255,255,255,.66);
              }
              #calendar-page .cc-calendar-main {min-height: 520px;}
              #calendar-page input, #calendar-page textarea, #calendar-page select {
                  border-radius: 12px !important;
              }

              /* Clean light dropdowns — remove Gradio's dark outer boxes / tiny white pills */
              #calendar-page .wrap,
              #calendar-page .secondary-wrap,
              #calendar-page .dropdown,
              #calendar-page [role="listbox"],
              #calendar-page [data-testid="dropdown"] {
                  background: #ffffff !important;
                  border: 1px solid rgba(120,120,140,.24) !important;
                  border-radius: 12px !important;
                  box-shadow: none !important;
                  color: #1f2430 !important;
              }

              #calendar-page .wrap-inner,
              #calendar-page .input-container,
              #calendar-page .container,
              #calendar-page .dropdown input,
              #calendar-page [role="combobox"] {
                  background: #ffffff !important;
                  color: #1f2430 !important;
                  border-radius: 12px !important;
                  box-shadow: none !important;
              }

              #calendar-page [role="combobox"] {
                  min-height: 42px !important;
                  width: 100% !important;
                  padding: 9px 12px !important;
                  border: 1px solid rgba(120,120,140,.24) !important;
              }

              #calendar-page .wrap:has([role="combobox"]),
              #calendar-page .secondary-wrap:has([role="combobox"]) {
                  padding: 0 !important;
                  background: transparent !important;
                  border: 0 !important;
              }

              /* Channel Coach dropdown theme: solid black with white text */
              #calendar-page [role="combobox"],
              #calendar-page .dropdown input,
              #calendar-page .wrap-inner:has([role="combobox"]),
              #calendar-page .input-container:has([role="combobox"]) {
                  background: #17181c !important;
                  color: #ffffff !important;
                  border-color: #17181c !important;
              }

              #calendar-page [role="combobox"] *,
              #calendar-page [role="combobox"] input,
              #calendar-page [role="combobox"] span {
                  color: #ffffff !important;
              }

              #calendar-page [role="combobox"] svg,
              #calendar-page .dropdown svg {
                  color: #ffffff !important;
                  fill: #ffffff !important;
                  stroke: #ffffff !important;
              }

              #calendar-page [role="combobox"]::placeholder,
              #calendar-page .dropdown input::placeholder {
                  color: rgba(255,255,255,.72) !important;
              }
            </style>
            <div class="cc-calendar-title"><h2>📅 Content Calendar</h2></div>
            <div class="cc-calendar-subtitle">
              Plan long videos, Shorts, Reels, TikToks, livestreams, and community posts.
            </div>
            """)

            with gr.Row(equal_height=False):
                with gr.Column(scale=1, min_width=300, elem_classes=["cc-card"]):
                    gr.Markdown("### ➕ Add Content")
                    cc_calendar_title = gr.Textbox(
                        label="Title",
                        placeholder="Example: Getting the Ice Rod"
                    )
                    cc_calendar_content_type = gr.Dropdown(
                        CONTENT_TYPES,
                        value="Long Video",
                        label="Content Type"
                    )
                    cc_calendar_game_topic = gr.Textbox(
                        label="Game / Topic",
                        placeholder="Example: Zelda ALTTP"
                    )
                    cc_calendar_status = gr.Dropdown(
                        CONTENT_STATUSES,
                        value="Idea",
                        label="Status"
                    )
                    cc_calendar_publish_date = gr.Textbox(
                        label="Target Publish Date",
                        value=date.today().isoformat(),
                        placeholder="YYYY-MM-DD"
                    )
                    cc_calendar_notes = gr.Textbox(
                        label="Notes",
                        lines=4,
                        placeholder="Example: Need thumbnail, voiceover, and final export."
                    )

                    cc_calendar_add_button = gr.Button("➕ Add to Calendar")
                    cc_calendar_message = gr.Textbox(label="Calendar Status", lines=2)

                    cc_upcoming_output = gr.HTML(value=render_upcoming_content(user_id="main"))

                    cc_plan_week_button = gr.Button("✨ Plan My Week")
                    cc_plan_week_output = gr.Textbox(label="Weekly Content Plan", lines=12)

                with gr.Column(scale=2, min_width=520):
                    gr.Markdown("### 🗓️ Schedule")
                    with gr.Row(elem_classes=["cc-toolbar"]):
                        cc_calendar_month = gr.Dropdown(
                            choices=list(range(1, 13)),
                            value=date.today().month,
                            label="Month"
                        )
                        cc_calendar_year = gr.Number(
                            value=date.today().year,
                            label="Year",
                            precision=0
                        )
                        cc_calendar_status_filter = gr.Dropdown(
                            ["All"] + CONTENT_STATUSES,
                            value="All",
                            label="Status Filter"
                        )
                        cc_calendar_type_filter = gr.Dropdown(
                            ["All"] + CONTENT_TYPES,
                            value="All",
                            label="Type Filter"
                        )

                    with gr.Column(elem_classes=["cc-card", "cc-calendar-main"]):
                        cc_calendar_output = gr.HTML(value=render_content_calendar(user_id="main"))
                    cc_calendar_refresh_button = gr.Button("🔄 Refresh Calendar")

            gr.Markdown("### ✏️ Edit or Delete Content")

            with gr.Column(elem_classes=["cc-card"]):
                cc_calendar_item_picker = gr.Dropdown(
                    choices=get_calendar_choices("main"),
                    label="Choose Calendar Item"
                )

                cc_calendar_load_button = gr.Button("📂 Load Selected Item")

                with gr.Row():
                    cc_calendar_update_button = gr.Button("💾 Save Edit")
                    cc_calendar_delete_button = gr.Button("🗑️ Delete Selected Item")

                cc_calendar_add_button.click(
                    add_content_item,
                    inputs=[
                        cc_calendar_title,
                        cc_calendar_content_type,
                        cc_calendar_game_topic,
                        cc_calendar_status,
                        cc_calendar_publish_date,
                        cc_calendar_notes,
                        workspace_name,
                        cc_calendar_month,
                        cc_calendar_year,
                        cc_calendar_status_filter,
                        cc_calendar_type_filter
                    ],
                    outputs=[cc_calendar_output, cc_upcoming_output, cc_calendar_item_picker, cc_calendar_message]
                )

                cc_calendar_refresh_button.click(
                    refresh_content_calendar,
                    inputs=[workspace_name, cc_calendar_month, cc_calendar_year, cc_calendar_status_filter, cc_calendar_type_filter],
                    outputs=[cc_calendar_output, cc_upcoming_output]
                )

                cc_calendar_month.change(
                    refresh_content_calendar,
                    inputs=[workspace_name, cc_calendar_month, cc_calendar_year, cc_calendar_status_filter, cc_calendar_type_filter],
                    outputs=[cc_calendar_output, cc_upcoming_output]
                )

                cc_calendar_year.change(
                    refresh_content_calendar,
                    inputs=[workspace_name, cc_calendar_month, cc_calendar_year, cc_calendar_status_filter, cc_calendar_type_filter],
                    outputs=[cc_calendar_output, cc_upcoming_output]
                )

                cc_calendar_status_filter.change(
                    refresh_content_calendar,
                    inputs=[workspace_name, cc_calendar_month, cc_calendar_year, cc_calendar_status_filter, cc_calendar_type_filter],
                    outputs=[cc_calendar_output, cc_upcoming_output]
                )

                cc_calendar_type_filter.change(
                    refresh_content_calendar,
                    inputs=[workspace_name, cc_calendar_month, cc_calendar_year, cc_calendar_status_filter, cc_calendar_type_filter],
                    outputs=[cc_calendar_output, cc_upcoming_output]
                )

                cc_calendar_load_button.click(
                    load_selected_content_item,
                    inputs=[cc_calendar_item_picker, workspace_name],
                    outputs=[
                        cc_calendar_title,
                        cc_calendar_content_type,
                        cc_calendar_game_topic,
                        cc_calendar_status,
                        cc_calendar_publish_date,
                        cc_calendar_notes,
                        cc_calendar_message
                    ]
                )

                cc_calendar_update_button.click(
                    update_content_item,
                    inputs=[
                        cc_calendar_item_picker,
                        cc_calendar_title,
                        cc_calendar_content_type,
                        cc_calendar_game_topic,
                        cc_calendar_status,
                        cc_calendar_publish_date,
                        cc_calendar_notes,
                        workspace_name,
                        cc_calendar_month,
                        cc_calendar_year,
                        cc_calendar_status_filter,
                        cc_calendar_type_filter
                    ],
                    outputs=[cc_calendar_output, cc_upcoming_output, cc_calendar_item_picker, cc_calendar_message]
                )

                cc_calendar_delete_button.click(
                    delete_content_item,
                    inputs=[
                        cc_calendar_item_picker,
                        workspace_name,
                        cc_calendar_month,
                        cc_calendar_year,
                        cc_calendar_status_filter,
                        cc_calendar_type_filter
                    ],
                    outputs=[cc_calendar_output, cc_upcoming_output, cc_calendar_item_picker, cc_calendar_message]
                )

                cc_plan_week_button.click(
                    plan_my_week,
                    inputs=[workspace_name],
                    outputs=cc_plan_week_output,
                    show_progress="full"
                )



        with gr.Column(visible=False, elem_id="projects-page") as projects_page:
            gr.Markdown("## 📁 Projects\n\nPlan your content, manage production, and open full workspaces for each video or Short.")

            with gr.Accordion("📅 Content Calendar", open=True):
                gr.Markdown(
                    """
                    ## 📅 Content Calendar
                    Plan your long videos, Shorts, livestreams, and community posts.

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
                        calendar_message = gr.Textbox(label="Calendar Status", lines=2)

                        upcoming_output = gr.HTML(value=render_upcoming_content(user_id="main"))

                        plan_week_button = gr.Button("✨ Plan My Week")
                        plan_week_output = gr.Textbox(label="Weekly Content Plan", lines=12)

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

                        calendar_output = gr.HTML(value=render_content_calendar(user_id="main"))
                        calendar_refresh_button = gr.Button("🔄 Refresh Calendar")

                gr.Markdown("### Edit or Delete Calendar Item")

                calendar_item_picker = gr.Dropdown(
                    choices=get_calendar_choices("main"),
                    label="Choose Calendar Item"
                )

                calendar_load_button = gr.Button("📂 Load Selected Item")

                with gr.Row():
                    calendar_update_button = gr.Button("💾 Save Edit")
                    calendar_delete_button = gr.Button("🗑️ Delete Selected Item")

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
                        calendar_type_filter
                    ],
                    outputs=[calendar_output, upcoming_output, calendar_item_picker, calendar_message]
                )

                calendar_refresh_button.click(
                    refresh_content_calendar,
                    inputs=[workspace_name, calendar_month, calendar_year, calendar_status_filter, calendar_type_filter],
                    outputs=[calendar_output, upcoming_output]
                )

                calendar_month.change(
                    refresh_content_calendar,
                    inputs=[workspace_name, calendar_month, calendar_year, calendar_status_filter, calendar_type_filter],
                    outputs=[calendar_output, upcoming_output]
                )

                calendar_year.change(
                    refresh_content_calendar,
                    inputs=[workspace_name, calendar_month, calendar_year, calendar_status_filter, calendar_type_filter],
                    outputs=[calendar_output, upcoming_output]
                )

                calendar_status_filter.change(
                    refresh_content_calendar,
                    inputs=[workspace_name, calendar_month, calendar_year, calendar_status_filter, calendar_type_filter],
                    outputs=[calendar_output, upcoming_output]
                )

                calendar_type_filter.change(
                    refresh_content_calendar,
                    inputs=[workspace_name, calendar_month, calendar_year, calendar_status_filter, calendar_type_filter],
                    outputs=[calendar_output, upcoming_output]
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
                        calendar_message
                    ]
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
                        calendar_type_filter
                    ],
                    outputs=[calendar_output, upcoming_output, calendar_item_picker, calendar_message]
                )

                calendar_delete_button.click(
                    delete_content_item,
                    inputs=[
                        calendar_item_picker,
                        workspace_name,
                        calendar_month,
                        calendar_year,
                        calendar_status_filter,
                        calendar_type_filter
                    ],
                    outputs=[calendar_output, upcoming_output, calendar_item_picker, calendar_message]
                )

                plan_week_button.click(
                    plan_my_week,
                    inputs=[workspace_name],
                    outputs=plan_week_output,
                    show_progress="full"
                )



            with gr.Accordion("🎬 Project Workspace", open=False):
                gr.Markdown(
                    """
                    ## 🎬 Project Workspace
                    Open any calendar item as a full creator project. Track real checklist progress, save notes, and generate project-specific guidance.
                    """
                )

                workspace_project_picker = gr.Dropdown(
                    choices=get_calendar_choices("main"),
                    label="Choose Project"
                )
                workspace_load_button = gr.Button("📂 Load Project")
                workspace_overview = gr.HTML(value=render_project_workspace_overview(None, "main"))

                with gr.Row():
                    with gr.Column(scale=1):
                        workspace_title = gr.Textbox(label="Project Title")
                        workspace_content_type = gr.Dropdown(CONTENT_TYPES, value="Long Video", label="Content Type")
                        workspace_game_topic = gr.Textbox(label="Game / Topic")
                        workspace_status = gr.Dropdown(CONTENT_STATUSES, value="Idea", label="Status")
                        workspace_publish_date = gr.Textbox(label="Target Publish Date", value=date.today().isoformat())

                        gr.Markdown("### Production Checklist")
                        workspace_script_written = gr.Checkbox(label="Script written")
                        workspace_gameplay_recorded = gr.Checkbox(label="Gameplay recorded")
                        workspace_voiceover_recorded = gr.Checkbox(label="Voiceover recorded")
                        workspace_editing_complete = gr.Checkbox(label="Editing complete")
                        workspace_thumbnail_finished = gr.Checkbox(label="Thumbnail finished")
                        workspace_description_done = gr.Checkbox(label="Description done")
                        workspace_uploaded_scheduled = gr.Checkbox(label="Uploaded / scheduled")
                        workspace_shared_social = gr.Checkbox(label="Shared on social media")

                        workspace_save_button = gr.Button("💾 Save Project Workspace")
                        workspace_message = gr.Textbox(label="Workspace Status", lines=2)

                    with gr.Column(scale=2):
                        workspace_project_notes = gr.Textbox(label="Project Notes", lines=6)
                        workspace_description_draft = gr.Textbox(label="Description Draft", lines=7)
                        workspace_thumbnail_notes = gr.Textbox(label="Thumbnail Notes", lines=5)
                        workspace_shorts_ideas_draft = gr.Textbox(label="Shorts Ideas / Clip Notes", lines=5)

                        gr.Markdown("### Project Assistant")
                        with gr.Row():
                            workspace_titles_button = gr.Button("✨ Generate Titles")
                            workspace_description_button = gr.Button("📝 Generate Description")
                            workspace_thumbnail_button = gr.Button("🖼 Thumbnail Ideas")

                        with gr.Row():
                            workspace_shorts_button = gr.Button("📱 Shorts Ideas")
                            workspace_review_button = gr.Button("🎬 Project Review")

                        workspace_ai_output = gr.Textbox(label="Project Results", lines=14)

                workspace_load_button.click(
                    load_project_workspace,
                    inputs=[workspace_project_picker, workspace_name],
                    outputs=[
                        workspace_overview,
                        workspace_title,
                        workspace_content_type,
                        workspace_game_topic,
                        workspace_status,
                        workspace_publish_date,
                        workspace_project_notes,
                        workspace_script_written,
                        workspace_gameplay_recorded,
                        workspace_voiceover_recorded,
                        workspace_editing_complete,
                        workspace_thumbnail_finished,
                        workspace_description_done,
                        workspace_uploaded_scheduled,
                        workspace_shared_social,
                        workspace_description_draft,
                        workspace_thumbnail_notes,
                        workspace_shorts_ideas_draft,
                        workspace_message
                    ]
                )

                workspace_save_button.click(
                    save_project_workspace,
                    inputs=[
                        workspace_project_picker,
                        workspace_title,
                        workspace_content_type,
                        workspace_game_topic,
                        workspace_status,
                        workspace_publish_date,
                        workspace_project_notes,
                        workspace_script_written,
                        workspace_gameplay_recorded,
                        workspace_voiceover_recorded,
                        workspace_editing_complete,
                        workspace_thumbnail_finished,
                        workspace_description_done,
                        workspace_uploaded_scheduled,
                        workspace_shared_social,
                        workspace_description_draft,
                        workspace_thumbnail_notes,
                        workspace_shorts_ideas_draft,
                        workspace_name
                    ],
                    outputs=[workspace_overview, workspace_project_picker, workspace_message]
                )

                workspace_titles_button.click(
                    project_generate_titles,
                    inputs=[workspace_project_picker, workspace_project_notes, workspace_description_draft, workspace_thumbnail_notes, workspace_shorts_ideas_draft, workspace_name],
                    outputs=workspace_ai_output,
                    show_progress="full"
                )

                workspace_description_button.click(
                    project_generate_description,
                    inputs=[workspace_project_picker, workspace_project_notes, workspace_description_draft, workspace_thumbnail_notes, workspace_shorts_ideas_draft, workspace_name],
                    outputs=workspace_ai_output,
                    show_progress="full"
                )

                workspace_thumbnail_button.click(
                    project_generate_thumbnail,
                    inputs=[workspace_project_picker, workspace_project_notes, workspace_description_draft, workspace_thumbnail_notes, workspace_shorts_ideas_draft, workspace_name],
                    outputs=workspace_ai_output,
                    show_progress="full"
                )

                workspace_shorts_button.click(
                    project_generate_shorts,
                    inputs=[workspace_project_picker, workspace_project_notes, workspace_description_draft, workspace_thumbnail_notes, workspace_shorts_ideas_draft, workspace_name],
                    outputs=workspace_ai_output,
                    show_progress="full"
                )

                workspace_review_button.click(
                    project_review,
                    inputs=[workspace_project_picker, workspace_project_notes, workspace_description_draft, workspace_thumbnail_notes, workspace_shorts_ideas_draft, workspace_name],
                    outputs=workspace_ai_output,
                    show_progress="full"
                )



        with gr.Column(visible=False, elem_id="toolkit-page") as toolkit_page:
            gr.Markdown("## 🎬 Creator Toolkit\n\nAnalyze videos, improve thumbnails, generate titles, optimize SEO, write descriptions, and brainstorm content ideas.")


            with gr.Accordion("💬 Coach Chat", open=True):
                gr.Markdown(
                    """
                    ## 💬 Coach Chat
                    Ask Channel Coach what to work on next, what to improve, or how to grow your channel.

                    Coach Chat uses your saved profile, calendar, projects, reviews, analytics, and Creator Health data.
                    """
                )

                coach_question = gr.Textbox(
                    label="Ask Coach Chat",
                    placeholder="Example: What should I work on today?",
                    lines=3
                )

                coach_button = gr.Button("Ask Coach")
                coach_output = gr.Markdown()

                coach_button.click(
                    ask_creator_coach,
                    inputs=[coach_question, workspace_name],
                    outputs=coach_output,
                    show_progress="full"
                )

            with gr.Accordion("🎥 Video Analyzer", open=True):
                gr.Markdown(
                    """
                    ## 🎥 Video Analyzer
                    Upload a long-form video, Short, Reel, TikTok, or Facebook Reel and get creator feedback. Channel Coach will sample frames and give pacing, hook, thumbnail, title, and editing advice.
                    """
                )

                analyzer_upload = gr.Video(label="Upload Video")

                analyzer_type = gr.Dropdown(
                    [
                        "Long-form YouTube Video",
                        "YouTube Short",
                        "TikTok",
                        "Instagram Reel",
                        "Facebook Reel"
                    ],
                    value="Long-form YouTube Video",
                    label="Video Type"
                )

                analyzer_notes = gr.Textbox(
                    label="Optional Notes",
                    lines=6,
                    placeholder="Example: This is my Ice Rod guide. Tell me what to cut, where to add text, and if the pacing feels good."
                )

                analyzer_button = gr.Button("🎥 Analyze Video")
                analyzer_output = gr.Textbox(label="Video Feedback", lines=18)


            with gr.Accordion("📚 Review History", open=False):
                review_history_output = gr.HTML(value=render_video_review_history("main"))
                review_history_refresh = gr.Button("🔄 Refresh Review History")

                review_history_refresh.click(
                    render_video_review_history,
                    inputs=[workspace_name],
                    outputs=review_history_output
                )

            analyzer_button.click(
                video_analyzer_with_history,
                inputs=[analyzer_upload, analyzer_notes, analyzer_type],
                outputs=[analyzer_output, review_history_output],
                show_progress="full"
            )


            with gr.Accordion("🧠 Creator Memory Insights", open=False):
                gr.Markdown(
                    """
                    Generate pattern-based insights from your saved video reviews. Channel Coach will look for repeated strengths, weak spots, score trends, and your next best focus.
                    """
                )
                creator_memory_snapshot = gr.HTML(value=render_creator_memory_snapshot())
                creator_memory_button = gr.Button("✨ Generate Creator Insights")
                creator_memory_output = gr.Textbox(label="Creator Memory Insights", lines=16)

                creator_memory_button.click(
                    generate_creator_memory_insights,
                    inputs=[],
                    outputs=creator_memory_output,
                    show_progress="full"
                )


            with gr.Accordion("🖼 Thumbnail Review", open=False):
                thumbnail_input = gr.Image(type="filepath", label="Upload Thumbnail")
                thumbnail_button = gr.Button("🖼 Review Thumbnail")
                thumbnail_output = gr.Textbox(label="Thumbnail Feedback", lines=16)

                thumbnail_button.click(
                    analyze_thumbnail,
                    inputs=[thumbnail_input, workspace_name],
                    outputs=thumbnail_output,
                    show_progress="full"
                )



            with gr.Accordion("🏷 Title Generator", open=False):
                title_input = gr.Textbox(label="Video Idea", lines=4)
                title_platform = gr.Dropdown(
                    ["YouTube Shorts", "TikTok", "Instagram Reels", "YouTube Long Form"],
                    value="YouTube Shorts",
                    label="Platform"
                )
                title_tone = gr.Dropdown(
                    ["Bold", "Funny", "Friendly", "Casual", "Professional"],
                    value="Bold",
                    label="Tone"
                )
                title_button = gr.Button("✨ Generate Titles")
                title_output = gr.Textbox(label="Title Ideas", lines=12)

                title_button.click(
                    generate_titles,
                    inputs=[title_input, title_platform, title_tone, workspace_name],
                    outputs=title_output,
                    show_progress="full"
                )


            with gr.Accordion("🔍 SEO Optimizer", open=False):
                seo_input = gr.Textbox(label="Video Idea", lines=4)
                seo_platform = gr.Dropdown(
                    ["YouTube Shorts", "TikTok", "Instagram Reels", "YouTube Long Form"],
                    value="YouTube Shorts",
                    label="Platform"
                )
                seo_niche = gr.Textbox(label="Niche", value="Gaming creator")
                seo_button = gr.Button("🔍 Generate SEO Plan")
                seo_output = gr.Textbox(label="SEO Results", lines=14)

                seo_button.click(
                    seo_help,
                    inputs=[seo_input, seo_platform, seo_niche, workspace_name],
                    outputs=seo_output,
                    show_progress="full"
                )


            with gr.Accordion("📝 Description Writer", open=False):
                desc_input = gr.Textbox(label="Video Idea", lines=4)
                desc_platform = gr.Dropdown(
                    ["YouTube Shorts", "TikTok", "Instagram Reels", "YouTube Long Form"],
                    value="YouTube Shorts",
                    label="Platform"
                )
                desc_niche = gr.Textbox(label="Niche", value="Gaming creator")
                desc_button = gr.Button("📝 Write Description")
                desc_output = gr.Textbox(label="Description", lines=14)

                desc_button.click(
                    description_help,
                    inputs=[desc_input, desc_platform, desc_niche, workspace_name],
                    outputs=desc_output,
                    show_progress="full"
                )


            with gr.Accordion("💡 Content Ideas", open=False):
                niche_input = gr.Textbox(label="Niche", value="Retro gaming")
                topic_input = gr.Textbox(label="Game or Topic", value="A Link to the Past")
                ideas_button = gr.Button("💡 Generate Ideas")
                ideas_output = gr.Textbox(label="Shorts Ideas", lines=16)

                ideas_button.click(
                    shorts_ideas,
                    inputs=[niche_input, topic_input, workspace_name],
                    outputs=ideas_output,
                    show_progress="full"
                )


        with gr.Column(visible=False, elem_id="analytics-page") as analytics_page:
            gr.Markdown("""
            ## 📊 Analytics Tracker
            Manually save your YouTube stats so Channel Coach can track growth over time.
            """)

            analytics_output = gr.HTML(value=render_analytics_tracker("main"))

            with gr.Accordion("➕ Add Analytics Snapshot", open=True):
                with gr.Row():
                    analytics_views = gr.Number(label="Total Views", value=0, precision=0)
                    analytics_subscribers = gr.Number(label="Subscribers", value=0, precision=0)
                with gr.Row():
                    analytics_watch_time = gr.Number(label="Watch Time Hours", value=0)
                    analytics_ctr = gr.Number(label="CTR %", value=0)

                analytics_notes = gr.Textbox(
                    label="Notes",
                    placeholder="Example: Posted 3 Shorts this week, Zelda guide performed well, took a 2-week break...",
                    lines=3
                )
                analytics_save_button = gr.Button("💾 Save Analytics Snapshot")
                analytics_status = gr.Markdown()

                analytics_save_button.click(
                    save_analytics_snapshot,
                    inputs=[analytics_views, analytics_subscribers, analytics_watch_time, analytics_ctr, analytics_notes, workspace_name],
                    outputs=[analytics_status, analytics_output]
                )

            analytics_refresh_button = gr.Button("🔄 Refresh Analytics")
            analytics_refresh_button.click(
                render_analytics_tracker,
                inputs=[workspace_name],
                outputs=analytics_output
            )

        with gr.Column(visible=False, elem_id="settings-page") as settings_page:
            gr.Markdown("## ⚙️ Settings\n\nManage your creator profile and app preferences.")

            with gr.Accordion("🚀 Getting Started", open=True):
                onboarding_output = gr.HTML(value=render_getting_started_checklist("main"))
                onboarding_refresh_button = gr.Button("🔄 Refresh Getting Started")

                onboarding_refresh_button.click(
                    render_getting_started_checklist,
                    inputs=[workspace_name],
                    outputs=onboarding_output
                )

            with gr.Accordion("👤 Creator Profile", open=True):
                gr.Markdown(
                    """
                    ## 👤 Creator Profile & Preferences
                    Save your channel niche, goals, style, and current content here.
                    Channel Coach will use this information in every tool.
                    """
                )

                profile_channel_name = gr.Textbox(
                    label="Channel Name",
                    value=saved_profile.get("channel_name", ""),
                    placeholder="Example: My Awesome Gaming Channel"
                )
                profile_creator_name = gr.Textbox(
                    label="Creator Name",
                    value=saved_profile.get("creator_name", ""),
                    placeholder="Example: Nicole, Alex, Gamer Mom, etc."
                )
                profile_niche = gr.Textbox(
                    label="Niche",
                    value=saved_profile.get("niche", ""),
                    placeholder="Example: Retro gaming, cooking, travel, tech reviews...",
                    lines=3
                )
                profile_target_audience = gr.Textbox(
                    label="Target Audience",
                    value=saved_profile.get("target_audience", ""),
                    placeholder="Example: Beginners, cozy gamers, busy parents, tech newbies...",
                    lines=3
                )
                profile_content_style = gr.Textbox(
                    label="Content Style",
                    value=saved_profile.get("content_style", ""),
                    placeholder="Example: Funny, helpful, cozy, direct, chaotic-good, cinematic...",
                    lines=3
                )
                profile_current_games = gr.Textbox(
                    label="Current Games / Current Content",
                    value=saved_profile.get("current_games", ""),
                    placeholder="Example: Stardew Valley guides, Zelda walkthroughs, budget recipes...",
                    lines=3
                )
                profile_main_platforms = gr.Textbox(
                    label="Main Platforms",
                    value=saved_profile.get("main_platforms", ""),
                    placeholder="Example: YouTube, TikTok, Instagram Reels, Facebook Reels"
                )
                profile_goals = gr.Textbox(
                    label="Goals",
                    value=saved_profile.get("goals", ""),
                    placeholder="Example: Grow subscribers, improve thumbnails, post 3 Shorts a week...",
                    lines=3
                )
                profile_preferred_tone = gr.Textbox(
                    label="Preferred Coaching Tone",
                    value=saved_profile.get("preferred_tone", ""),
                    placeholder="Example: Friendly, honest, motivating, not too corporate...",
                    lines=3
                )
                profile_things_to_avoid = gr.Textbox(
                    label="Things Channel Coach Should Avoid",
                    value=saved_profile.get("things_to_avoid", ""),
                    placeholder="Example: Fake clickbait, generic advice, too much jargon...",
                    lines=3
                )

                profile_save_button = gr.Button("💾 Save Creator Profile")
                profile_save_status = gr.Textbox(label="Save Status", lines=2)

                profile_save_button.click(
                    save_creator_profile_and_refresh_dashboard,
                    inputs=[
                        profile_channel_name,
                        profile_creator_name,
                        profile_niche,
                        profile_target_audience,
                        profile_content_style,
                        profile_current_games,
                        profile_main_platforms,
                        profile_goals,
                        profile_preferred_tone,
                        profile_things_to_avoid,
                        workspace_name
                    ],
                    outputs=[profile_save_status, dashboard_output, onboarding_output]
                )



    # =========================
    # PAGE NAVIGATION
    # =========================
    def toggle_menu(is_open):
        new_state = not is_open
        return new_state, gr.update(visible=new_state)

    def show_page(page_name):
        names = ["chat", "dashboard", "calendar", "projects", "toolkit", "analytics", "settings"]
        return (
            [gr.update(visible=(name == page_name)) for name in names]
            + [gr.update(visible=False), False]
        )

    page_outputs = [
        chat_page,
        dashboard_page,
        calendar_page,
        projects_page,
        toolkit_page,
        analytics_page,
        settings_page,
        menu_panel,
        menu_open,
    ]

    menu_button.click(
        toggle_menu,
        inputs=[menu_open],
        outputs=[menu_open, menu_panel]
    )
    chat_nav.click(lambda: show_page("chat"), outputs=page_outputs)
    dashboard_nav.click(lambda: show_page("dashboard"), outputs=page_outputs)
    calendar_nav.click(lambda: show_page("calendar"), outputs=page_outputs)
    projects_nav.click(lambda: show_page("projects"), outputs=page_outputs)
    toolkit_nav.click(lambda: show_page("toolkit"), outputs=page_outputs)
    analytics_nav.click(lambda: show_page("analytics"), outputs=page_outputs)
    settings_nav.click(lambda: show_page("settings"), outputs=page_outputs)

    home_chat_button.click(
        ask_creator_coach,
        inputs=[home_chat_question, workspace_name],
        outputs=home_chat_output,
        show_progress="full"
    )

    def login_and_open_app(email, password, remember):
        email = (email or "").strip()
        password = password or ""

        if not email or not password:
            return (
                "Enter both your email and password.",
                "",
                empty_saved_session(),
                gr.update(visible=True),
                gr.update(visible=False),
            )

        message, user_id, session = login_user(email, password)
        logged_in = bool(user_id)
        saved_session = session if (logged_in and remember) else empty_saved_session()

        return (
            message,
            user_id or "",
            saved_session,
            gr.update(visible=not logged_in),
            gr.update(visible=logged_in),
        )

    def restore_and_open_app(saved_session):
        message, user_id, session = restore_saved_session(saved_session)
        logged_in = bool(user_id)
        return (
            message,
            user_id,
            session,
            gr.update(visible=not logged_in),
            gr.update(visible=logged_in),
        )

    workspace_button.click(
        load_workspace_ui,
        inputs=[workspace_name],
        outputs=[
            workspace_indicator,
            dashboard_output,
            cc_calendar_output,
            cc_upcoming_output,
            cc_calendar_item_picker,
            calendar_item_picker,
            workspace_project_picker,
            analytics_output,
            onboarding_output,
            profile_channel_name,
            profile_creator_name,
            profile_niche,
            profile_target_audience,
            profile_content_style,
            profile_current_games,
            profile_main_platforms,
            profile_goals,
            profile_preferred_tone,
            profile_things_to_avoid
        ]
    )

    login_button.click(
        login_and_open_app,
        inputs=[login_email, login_password, remember_me],
        outputs=[login_status, workspace_name, saved_login, login_screen, app_shell],
        show_progress="full"
    ).then(
        load_workspace_ui,
        inputs=[workspace_name],
        outputs=[
            workspace_indicator,
            dashboard_output,
            cc_calendar_output,
            cc_upcoming_output,
            cc_calendar_item_picker,
            calendar_item_picker,
            workspace_project_picker,
            analytics_output,
            onboarding_output,
            profile_channel_name,
            profile_creator_name,
            profile_niche,
            profile_target_audience,
            profile_content_style,
            profile_current_games,
            profile_main_platforms,
            profile_goals,
            profile_preferred_tone,
            profile_things_to_avoid
        ]
    )

    signup_button.click(
        signup_user,
        inputs=[login_email, login_password],
        outputs=login_status,
        show_progress="full"
    )
    app.load(
        restore_and_open_app,
        inputs=[saved_login],
        outputs=[login_status, workspace_name, saved_login, login_screen, app_shell],
    ).then(
        load_workspace_ui,
        inputs=[workspace_name],
        outputs=[
            workspace_indicator,
            dashboard_output,
            cc_calendar_output,
            cc_upcoming_output,
            cc_calendar_item_picker,
            calendar_item_picker,
            workspace_project_picker,
            analytics_output,
            onboarding_output,
            profile_channel_name,
            profile_creator_name,
            profile_niche,
            profile_target_audience,
            profile_content_style,
            profile_current_games,
            profile_main_platforms,
            profile_goals,
            profile_preferred_tone,
            profile_things_to_avoid
        ]
    )

# =========================
# SERVE PWA FILES
# =========================
# These lines make Gradio serve your app icon files and PWA files.

app.app.mount("/static", StaticFiles(directory="static"), name="static")


@app.app.get("/manifest.json", include_in_schema=False)
async def serve_manifest():
    return FileResponse("manifest.json", media_type="application/manifest+json")


@app.app.get("/service-worker.js", include_in_schema=False)
async def serve_service_worker():
    return FileResponse("service-worker.js", media_type="application/javascript")


port = int(os.environ.get("PORT", 7860))

app.launch(
    server_name="0.0.0.0",
    server_port=port,
    share=False
)





    
 
        
 
      
 
      
    
 
      
    
 
      


    
 
      
 
      
    
 
      
      
    
 
      
    
 
      
