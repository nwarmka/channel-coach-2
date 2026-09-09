# Channel Coach main app
# UI lives here. Feature functions, styles, constants, and helpers are imported from features.py.

from features import *
from ui.calendar import build_calendar_page
from ui.dashboard import build_dashboard_page
from ui.toolkit import build_toolkit_page
from ui.analytics import build_analytics_page
from ui.settings import build_settings_page
from ui.chat import build_chat_page
from auth import (
    empty_saved_session,
    login_user,
    logout_user,
    request_password_reset,
    restore_saved_session,
    signup_user,
)


with gr.Blocks(title="Channel Coach") as app:

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
      position:fixed!important; right:22px!important; left:auto!important; top:82px!important; z-index:9999!important;
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

    /* =========================
       FULL PAGE COACH CHAT
       ========================= */

    #chat-page{
      width:100%!important;
      max-width:none!important;
      height:calc(100vh - 105px)!important;
      min-height:650px!important;
      margin:0!important;
      padding:0!important;
      border:0!important;
      border-radius:0!important;
      background:transparent!important;
      box-shadow:none!important;
    }

    #coach-chat-header{
      max-width:900px!important;
      width:100%!important;
      margin:0 auto!important;
      padding:8px 18px 10px!important;
    }

    .cc-chat-title{
      display:flex;
      align-items:center;
      gap:10px;
      color:#f7f7fb;
      font-size:.9rem;
      font-weight:900;
      letter-spacing:.12em;
    }

    .cc-chat-orb{
      color:var(--cyan);
      text-shadow:
        0 0 12px rgba(22,217,255,.65),
        0 0 24px rgba(139,92,246,.35);
    }

    #coach-chatbot{
      width:100%!important;
      max-width:900px!important;
      margin:0 auto!important;
      flex:1 1 auto!important;
      background:transparent!important;
      border:0!important;
      box-shadow:none!important;
    }

    #coach-chatbot > div{
      background:transparent!important;
      border:0!important;
      box-shadow:none!important;
    }

    #coach-chatbot .message{
      border-radius:18px!important;
      line-height:1.55!important;
    }

    #coach-chatbot .message.user,
    #coach-chatbot [data-testid="user"]{
      background:linear-gradient(
        135deg,
        rgba(139,92,246,.30),
        rgba(255,62,165,.22)
      )!important;
      border:1px solid rgba(255,62,165,.30)!important;
      color:#fff!important;
    }

    #coach-chatbot .message.bot,
    #coach-chatbot .message.assistant,
    #coach-chatbot [data-testid="bot"]{
      background:transparent!important;
      border:0!important;
      color:#f3f5fb!important;
    }

    #coach-chat-composer{
      width:calc(100% - 28px)!important;
      max-width:900px!important;
      margin:10px auto 16px!important;
      padding:9px 10px!important;
      background:#10131c!important;
      border:1px solid rgba(139,92,246,.48)!important;
      border-radius:22px!important;
      box-shadow:
        0 12px 36px rgba(0,0,0,.38),
        0 0 20px rgba(139,92,246,.08)!important;
    }

    #coach-chat-input{
      background:transparent!important;
      border:0!important;
      box-shadow:none!important;
    }

    #coach-chat-input textarea{
      background:transparent!important;
      border:0!important;
      box-shadow:none!important;
      color:#fff!important;
      min-height:46px!important;
      padding:12px 8px!important;
      resize:none!important;
    }

    #coach-chat-input textarea:focus{
      border:0!important;
      box-shadow:none!important;
    }

    #coach-chat-send{
      width:48px!important;
      min-width:48px!important;
      height:48px!important;
      padding:0!important;
      border-radius:50%!important;
      background:linear-gradient(
        135deg,
        var(--purple),
        var(--pink)
      )!important;
      border:0!important;
      box-shadow:0 0 22px rgba(255,62,165,.25)!important;
      font-size:1.25rem!important;
    }

    #coach-chat-send:hover{
      transform:scale(1.04)!important;
      box-shadow:0 0 28px rgba(255,62,165,.38)!important;
    }

    @media(max-width:700px){
      #chat-page{
        height:calc(100vh - 85px)!important;
        min-height:560px!important;
      }

      #coach-chat-header{
        padding-left:8px!important;
        padding-right:8px!important;
      }

      #coach-chatbot{
        max-width:100%!important;
      }

      #coach-chat-composer{
        width:calc(100% - 12px)!important;
        margin-bottom:8px!important;
      }
    }

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

    #login-screen input,
    #login-screen textarea,
    #login-screen .wrap,
    #login-screen .wrap-inner,
    #login-screen .input-container,
    #login-screen .secondary-wrap{
      background:#05070d!important;
      color:#ffffff!important;
      border-color:#ffffff!important;
      box-shadow:none!important;
    }

    #login-screen input{
      background:#05070d!important;
      color:#ffffff!important;
      border:1px solid #ffffff!important;
      border-radius:12px!important;
      min-height:48px!important;
      -webkit-text-fill-color:#ffffff!important;
    }

    #login-screen input:-webkit-autofill,
    #login-screen input:-webkit-autofill:hover,
    #login-screen input:-webkit-autofill:focus{
      -webkit-box-shadow:0 0 0 1000px #05070d inset!important;
      -webkit-text-fill-color:#ffffff!important;
      caret-color:#ffffff!important;
      border:1px solid #ffffff!important;
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

    /* Remember Me: make the checked state obvious on desktop and installed mobile/PWA */
    #remember-me{
      background:transparent!important;
      border:0!important;
      box-shadow:none!important;
    }

    #remember-me input[type="checkbox"]{
      appearance:auto!important;
      -webkit-appearance:checkbox!important;
      width:20px!important;
      height:20px!important;
      min-height:20px!important;
      accent-color:#ff3ea5!important;
      cursor:pointer!important;
    }

    #remember-me input[type="checkbox"]:checked{
      accent-color:#ff3ea5!important;
      filter:drop-shadow(0 0 5px rgba(255,62,165,.65));
    }

    #remember-me label{
      color:#eef1f8!important;
      cursor:pointer!important;
    }

    #login-status{
      padding:8px 2px 0!important;
    }

    #login-status p{
      color:#dbe2f2!important;
    }


    /* Clean cyberpunk form system: no white label caps */
    #channel-coach-app label,
    #channel-coach-app .label-wrap,
    #channel-coach-app .label-wrap > span,
    #channel-coach-app .block-info,
    #channel-coach-app .block-title,
    #channel-coach-app span[data-testid="block-info"] {
      background: transparent !important;
      background-color: transparent !important;
      color: #e8ebf5 !important;
      border: 0 !important;
      box-shadow: none !important;
    }

    #channel-coach-app .label-wrap {
      padding: 0 2px 7px !important;
      margin: 0 !important;
    }

    #channel-coach-app .wrap,
    #channel-coach-app .secondary-wrap,
    #channel-coach-app .input-container,
    #channel-coach-app .wrap-inner {
      background: transparent !important;
      border: 0 !important;
      box-shadow: none !important;
    }

    #channel-coach-app input,
    #channel-coach-app textarea,
    #channel-coach-app select,
    #channel-coach-app [role="combobox"] {
      width: 100% !important;
      background: #050810 !important;
      color: #ffffff !important;
      -webkit-text-fill-color: #ffffff !important;
      border: 1px solid rgba(139,92,246,.72) !important;
      border-radius: 11px !important;
      min-height: 46px !important;
      box-shadow: 0 0 12px rgba(139,92,246,.05) !important;
    }

    #channel-coach-app input::placeholder,
    #channel-coach-app textarea::placeholder {
      color: #69738b !important;
      -webkit-text-fill-color: #69738b !important;
      opacity: 1 !important;
    }

    #channel-coach-app input:focus,
    #channel-coach-app textarea:focus,
    #channel-coach-app select:focus,
    #channel-coach-app [role="combobox"]:focus-within {
      outline: none !important;
      border-color: var(--cyan) !important;
      box-shadow: 0 0 0 2px rgba(22,217,255,.09), 0 0 18px rgba(22,217,255,.13) !important;
    }

    #channel-coach-app [role="combobox"] *,
    #channel-coach-app .dropdown input,
    #channel-coach-app .dropdown span {
      color: #ffffff !important;
      -webkit-text-fill-color: #ffffff !important;
    }

    #channel-coach-app [role="combobox"] svg,
    #channel-coach-app .dropdown svg {
      color: #dfe6ff !important;
      fill: currentColor !important;
      stroke: currentColor !important;
    }

    /* Calendar gets one clean neon panel per section, not a box around each control */
    #calendar-page .cc-card,
    #calendar-page .cc-toolbar {
      padding: 18px !important;
      background: rgba(7,10,17,.88) !important;
      border: 1px solid rgba(255,62,165,.32) !important;
      border-radius: 16px !important;
    }

    #calendar-page .cc-toolbar .block,
    #calendar-page .cc-card .block {
      background: transparent !important;
      border: 0 !important;
      box-shadow: none !important;
    }

    #channel-coach-app input:-webkit-autofill,
    #channel-coach-app input:-webkit-autofill:hover,
    #channel-coach-app input:-webkit-autofill:focus {
      -webkit-box-shadow: 0 0 0 1000px #050810 inset !important;
      -webkit-text-fill-color: #ffffff !important;
      caret-color: #ffffff !important;
    }


    /* Definitive form styling using manual labels (no Gradio label caps) */
    #channel-coach-app .cc-field-label {
      color:#f5f7ff !important;
      font-size:.86rem !important;
      font-weight:700 !important;
      margin:10px 0 7px 2px !important;
      padding:0 !important;
      background:transparent !important;
      letter-spacing:.01em !important;
    }

    #channel-coach-app .cc-cyber-field {
      background:transparent !important;
      border:0 !important;
      box-shadow:none !important;
      padding:0 !important;
    }

    #channel-coach-app .cc-cyber-field > div,
    #channel-coach-app .cc-cyber-field .wrap,
    #channel-coach-app .cc-cyber-field .wrap-inner,
    #channel-coach-app .cc-cyber-field .secondary-wrap,
    #channel-coach-app .cc-cyber-field .input-container {
      background:transparent !important;
      border:0 !important;
      box-shadow:none !important;
    }

    #channel-coach-app .cc-cyber-field input,
    #channel-coach-app .cc-cyber-field textarea,
    #channel-coach-app .cc-cyber-field [role="combobox"] {
      background:#050810 !important;
      color:#ffffff !important;
      -webkit-text-fill-color:#ffffff !important;
      border:1px solid rgba(139,92,246,.78) !important;
      border-radius:11px !important;
      min-height:46px !important;
      box-shadow:0 0 14px rgba(139,92,246,.06) !important;
    }

    #channel-coach-app .cc-cyber-field input:focus,
    #channel-coach-app .cc-cyber-field textarea:focus,
    #channel-coach-app .cc-cyber-field [role="combobox"]:focus-within {
      border-color:#16d9ff !important;
      box-shadow:0 0 0 2px rgba(22,217,255,.09),0 0 18px rgba(22,217,255,.15) !important;
    }

    #channel-coach-app .cc-cyber-field [role="combobox"] *,
    #channel-coach-app .cc-cyber-field [role="combobox"] span {
      color:#ffffff !important;
      -webkit-text-fill-color:#ffffff !important;
    }

    #channel-coach-app .cc-cyber-field [role="combobox"] svg {
      color:#ffffff !important;
      stroke:#ffffff !important;
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
    # One stable key/secret is important for desktop AND the installed PWA.
    # Set CHANNEL_COACH_BROWSER_SECRET once in Render and do not rotate it
    # unless you intentionally want every remembered device to sign in again.
    browser_secret = os.environ.get(
        "CHANNEL_COACH_BROWSER_SECRET",
        "channel-coach-browser-state-v2",
    )

    saved_login = gr.BrowserState(
        default_value=empty_saved_session(),
        storage_key="channel_coach_login_v2",
        secret=browser_secret,
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

        forgot_password_button = gr.Button(
            "FORGOT PASSWORD?",
            elem_id="forgot-password-button"
        )

        login_status = gr.Markdown(elem_id="login-status")

    with gr.Column(visible=False, elem_id="channel-coach-app") as app_shell:
        # =========================
        # APP SHELL / NAVIGATION
        # =========================
        with gr.Row():
            gr.Markdown("## ✦ CHANNEL COACH")
            menu_button = gr.Button("☰", scale=0, min_width=52)

        with gr.Column(visible=False, elem_id="channel-coach-menu") as menu_panel:
            home_nav = gr.Button("🏠 Home")
            back_nav = gr.Button("← Back")
            chat_nav = gr.Button("💬 Coach Chat")
            dashboard_nav = gr.Button("📊 Dashboard")
            calendar_nav = gr.Button("📅 Calendar")
            toolkit_nav = gr.Button("🎬 Toolkit")
            analytics_nav = gr.Button("📊 Analytics")
            settings_nav = gr.Button("⚙️ Settings")
            logout_button = gr.Button("↪️ Log Out")

        menu_open = gr.State(False)
        current_page = gr.State("dashboard")
        previous_page = gr.State("dashboard")

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

        # Coach Chat is available from the menu.
        # Creator Dashboard remains the logged-in home screen.
        chat_page = build_chat_page(
            workspace_name,
            visible=False,
        )

        dashboard_page, dashboard_output = build_dashboard_page(
            workspace_name,
            visible=True,
        )

        def load_workspace_ui(current_workspace):
            # Never load the shared/default workspace for a logged-out visitor.
            # Login/restore must provide a real Supabase user ID first.
            if not current_workspace:
                return (
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    gr.update(),
                )

            safe_workspace = current_workspace
            profile = load_creator_profile(safe_workspace)
            return (
                f"Current workspace: **{safe_workspace}**",
                render_creator_dashboard(safe_workspace),
                render_content_calendar(user_id=safe_workspace),
                render_upcoming_content(user_id=safe_workspace),
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




        (
            calendar_page,
            cc_calendar_output,
            cc_upcoming_output,
            cc_calendar_item_picker,
        ) = build_calendar_page(
            workspace_name,
            visible=False,
        )

        toolkit_page = build_toolkit_page(
            workspace_name,
            visible=False,
        )

        analytics_page, analytics_output = build_analytics_page(
            workspace_name,
            visible=False,
        )

        settings_components = build_settings_page(
            workspace_name,
            dashboard_output,
            visible=False,
        )

        settings_page = settings_components["page"]
        onboarding_output = settings_components["onboarding_output"]
        profile_channel_name = settings_components["profile_channel_name"]
        profile_creator_name = settings_components["profile_creator_name"]
        profile_niche = settings_components["profile_niche"]
        profile_target_audience = settings_components["profile_target_audience"]
        profile_content_style = settings_components["profile_content_style"]
        profile_current_games = settings_components["profile_current_games"]
        profile_main_platforms = settings_components["profile_main_platforms"]
        profile_goals = settings_components["profile_goals"]
        profile_preferred_tone = settings_components["profile_preferred_tone"]
        profile_things_to_avoid = settings_components["profile_things_to_avoid"]

    # =========================
    # PAGE NAVIGATION
    # =========================
    PAGE_NAMES = ["chat", "dashboard", "calendar", "toolkit", "analytics", "settings"]

    def toggle_menu(is_open):
        new_state = not bool(is_open)
        return new_state, gr.update(visible=new_state)

    def navigate_to(page_name, current):
        target = page_name if page_name in PAGE_NAMES else "dashboard"
        current = current if current in PAGE_NAMES else "dashboard"
        previous = current if current != target else current
        return (
            *[gr.update(visible=(name == target)) for name in PAGE_NAMES],
            gr.update(visible=False),
            False,
            target,
            previous,
        )

    def navigate_back(current, previous):
        current = current if current in PAGE_NAMES else "dashboard"
        target = previous if previous in PAGE_NAMES else "dashboard"
        return (
            *[gr.update(visible=(name == target)) for name in PAGE_NAMES],
            gr.update(visible=False),
            False,
            target,
            current,
        )

    def reset_navigation():
        return (
            *[gr.update(visible=(name == "dashboard")) for name in PAGE_NAMES],
            gr.update(visible=False),
            False,
            "dashboard",
            "dashboard",
        )

    page_outputs = [
        chat_page,
        dashboard_page,
        calendar_page,
        toolkit_page,
        analytics_page,
        settings_page,
        menu_panel,
        menu_open,
        current_page,
        previous_page,
    ]

    menu_button.click(
        toggle_menu,
        inputs=[menu_open],
        outputs=[menu_open, menu_panel],
        show_progress="hidden",
    )

    home_nav.click(
        lambda current: navigate_to("dashboard", current),
        inputs=[current_page],
        outputs=page_outputs,
        show_progress="hidden",
    )
    back_nav.click(
        navigate_back,
        inputs=[current_page, previous_page],
        outputs=page_outputs,
        show_progress="hidden",
    )
    chat_nav.click(
        lambda current: navigate_to("chat", current),
        inputs=[current_page],
        outputs=page_outputs,
        show_progress="hidden",
    )
    dashboard_nav.click(
        lambda current: navigate_to("dashboard", current),
        inputs=[current_page],
        outputs=page_outputs,
        show_progress="hidden",
    )
    calendar_nav.click(
        lambda current: navigate_to("calendar", current),
        inputs=[current_page],
        outputs=page_outputs,
        show_progress="hidden",
    )
    toolkit_nav.click(
        lambda current: navigate_to("toolkit", current),
        inputs=[current_page],
        outputs=page_outputs,
        show_progress="hidden",
    )
    analytics_nav.click(
        lambda current: navigate_to("analytics", current),
        inputs=[current_page],
        outputs=page_outputs,
        show_progress="hidden",
    )
    settings_nav.click(
        lambda current: navigate_to("settings", current),
        inputs=[current_page],
        outputs=page_outputs,
        show_progress="hidden",
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
            user_id or "",
            session if logged_in else empty_saved_session(),
            gr.update(visible=not logged_in),
            gr.update(visible=logged_in),
        )

    def logout_and_close_app(saved_session):
        message, _, cleared = logout_user(saved_session)
        return (
            message,
            "",
            cleared,
            gr.update(visible=True),
            gr.update(visible=False),
            False,
            gr.update(visible=False),
            "dashboard",
            "dashboard",
        )

    def send_password_reset(email):
        redirect_to = os.environ.get("CHANNEL_COACH_PASSWORD_RESET_REDIRECT", "").strip()
        return request_password_reset(email, redirect_to or None)

    workspace_button.click(
        load_workspace_ui,
        inputs=[workspace_name],
        outputs=[
            workspace_indicator,
            dashboard_output,
            cc_calendar_output,
            cc_upcoming_output,
            cc_calendar_item_picker,
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
        reset_navigation,
        outputs=page_outputs,
        show_progress="hidden",
    ).then(
        load_workspace_ui,
        inputs=[workspace_name],
        outputs=[
            workspace_indicator,
            dashboard_output,
            cc_calendar_output,
            cc_upcoming_output,
            cc_calendar_item_picker,
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
    forgot_password_button.click(
        send_password_reset,
        inputs=[login_email],
        outputs=login_status,
        show_progress="hidden",
    )

    logout_button.click(
        logout_and_close_app,
        inputs=[saved_login],
        outputs=[
            login_status,
            workspace_name,
            saved_login,
            login_screen,
            app_shell,
            menu_open,
            menu_panel,
            current_page,
            previous_page,
        ],
        show_progress="hidden",
    )
    app.load(
        restore_and_open_app,
        inputs=[saved_login],
        outputs=[login_status, workspace_name, saved_login, login_screen, app_shell],
    ).then(
        reset_navigation,
        outputs=page_outputs,
        show_progress="hidden",
    ).then(
        load_workspace_ui,
        inputs=[workspace_name],
        outputs=[
            workspace_indicator,
            dashboard_output,
            cc_calendar_output,
            cc_upcoming_output,
            cc_calendar_item_picker,
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
    share=False,
    head=custom_head,
    css=custom_css,
)











    
 
        
 
      
 
      
    
 
      
    
 
      


    
 
      
 
      
    
 
      
      
    
 
      
    
 
      
