# Channel Coach main app
# UI lives here. Feature functions, styles, constants, and helpers are imported from features.py.

from features import *
from ui.calendar import build_calendar_page
from ui.dashboard import build_dashboard_page
from ui.toolkit import build_toolkit_page
from ui.settings import build_settings_page
from ui.chat import build_chat_page
from ui.bug_report import build_bug_report_page
from ui.bug_admin import admin_button_visibility, build_bug_admin_page
from credits import ensure_initial_credits, get_credit_balance
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
       PAGE WIDTHS
       Coach Chat styling now lives entirely in ui/chat.py.
       ========================= */

    #calendar-page,#dashboard-page,#projects-page,#toolkit-page,#settings-page{
      max-width:1400px!important;margin:0 auto!important;
    }

    #calendar-page h2,#dashboard-page h2,#projects-page h2,#toolkit-page h2,#settings-page h2{
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

    /* Dashboard task navigation bridge must stay rendered so clicks can reach Gradio. */
    #dashboard-task-nav,
    #dashboard-task-bridge {
      position: fixed !important;
      left: -10000px !important;
      top: -10000px !important;
      width: 1px !important;
      height: 1px !important;
      min-height: 0 !important;
      overflow: hidden !important;
      opacity: 0 !important;
      pointer-events: none !important;
      border: 0 !important;
      padding: 0 !important;
      margin: 0 !important;
    }

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
    
    /* Darker, quieter section borders */
    #channel-coach-app .gr-box,
    #channel-coach-app .block,
    #channel-coach-app .panel,
    #channel-coach-app .form,
    #channel-coach-app .cc-card,
    #channel-coach-app .cc-toolbar {
      border-color: rgba(125, 24, 91, 0.80) !important;
    }

    #channel-coach-app #dashboard-page .cc-dashboard-page-header {
      border-color: rgba(125, 24, 91, 0.80) !important;
    }

    #channel-coach-app #dashboard-page {
      border-color: rgba(125, 24, 91, 0.80) !important;
    }

    
    /* Dark magenta borders for dashboard bubbles/cards */
    #channel-coach-app #dashboard-output .cc-dashboard-hero,
    #channel-coach-app #dashboard-output .cc-dashboard-stat,
    #channel-coach-app #dashboard-output .cc-dashboard-panel,
    #channel-coach-app #dashboard-output .cc-dashboard-grid,
    #channel-coach-app #dashboard-output .cc-dashboard-two-col,
    #channel-coach-app #dashboard-output .cc-dashboard-full-stack,
    #channel-coach-app #dashboard-output .cc-planner-wrap {
      border-color: rgba(125, 24, 91, 0.80) !important;
    }

    
    /* True-black background with thicker dark-pink section borders */
    html,
    body,
    .gradio-container,
    #channel-coach-app {
      background: #000000 !important;
    }

    #channel-coach-app .gr-box,
    #channel-coach-app .block,
    #channel-coach-app .panel,
    #channel-coach-app .form,
    #channel-coach-app .cc-card,
    #channel-coach-app .cc-toolbar,
    #channel-coach-app #dashboard-page .cc-dashboard-page-header {
      border-width: 2px !important;
      border-style: solid !important;
      border-color: rgba(125, 24, 91, 0.88) !important;
    }

    #channel-coach-app #dashboard-output .cc-dashboard-hero,
    #channel-coach-app #dashboard-output .cc-dashboard-stat,
    #channel-coach-app #dashboard-output .cc-dashboard-panel,
    #channel-coach-app #dashboard-output .cc-dashboard-grid,
    #channel-coach-app #dashboard-output .cc-dashboard-two-col,
    #channel-coach-app #dashboard-output .cc-dashboard-full-stack,
    #channel-coach-app #dashboard-output .cc-planner-wrap {
      border-width: 2px !important;
      border-style: solid !important;
      border-color: rgba(125, 24, 91, 0.88) !important;
    }

    /* Dashboard's outer Gradio column: no surrounding border/card.
       Leave its inner section panels and task cards unchanged. */
    #channel-coach-app #dashboard-page {
      border: 0 !important;
      outline: 0 !important;
      box-shadow: none !important;
      background: transparent !important;
    }


    /* Compact, unified app header; keep the borderless Dashboard unchanged. */
    #channel-coach-app #cc-top-header {
      display: flex !important;
      flex-wrap: nowrap !important;
      align-items: center !important;
      gap: 14px !important;
      padding: 14px 20px !important;
      background: #0d101a !important;
      border: 1px solid rgba(255,62,165,.45) !important;
      border-radius: 18px !important;
      box-shadow: 0 8px 28px rgba(0,0,0,.25) !important;
    }
    #channel-coach-app #cc-header-brand {
      flex: 1 1 auto !important;
      min-width: 0 !important;
      width: auto !important;
      margin: 0 !important;
      padding: 0 !important;
      background: transparent !important;
      border: 0 !important;
      box-shadow: none !important;
    }
    #channel-coach-app #cc-header-brand p {
      margin: 0 !important;
      color: #fff !important;
      font-size: 1.4rem !important;
      font-weight: 900 !important;
      letter-spacing: .05em !important;
      white-space: nowrap;
    }
    #channel-coach-app #credit-balance {
      flex: 0 0 auto !important;
      width: auto !important;
      min-width: 0 !important;
      margin: 0 !important;
      padding: 9px 16px !important;
      background: rgba(255,62,165,.09) !important;
      border: 1px solid rgba(255,62,165,.5) !important;
      border-radius: 999px !important;
      box-shadow: none !important;
    }
    #channel-coach-app #credit-balance p {
      margin: 0 !important;
      color: #fff !important;
      font-size: .95rem !important;
      white-space: nowrap;
    }
    #channel-coach-app #cc-header-menu {
      flex: 0 0 48px !important;
      width: 48px !important;
      min-width: 48px !important;
      height: 44px !important;
      font-size: 1.4rem !important;
      border-radius: 12px !important;
    }
    @media (max-width: 600px) {
      #channel-coach-app #cc-top-header { padding: 12px !important; gap: 8px !important; }
      #channel-coach-app #cc-header-brand p { font-size: 1rem !important; letter-spacing: 0 !important; }
      #channel-coach-app #credit-balance { padding: 8px !important; }
      #channel-coach-app #credit-balance p { font-size: .8rem !important; }
      #channel-coach-app #cc-header-menu { flex-basis: 42px !important; width: 42px !important; min-width: 42px !important; }
    }


    /* Gaming-inspired brand lockup: isolated to the app header. */
    #channel-coach-app #cc-top-header {
      position: relative !important;
      overflow: hidden !important;
      padding-bottom: 18px !important;
    }
    #channel-coach-app #cc-top-header::after {
      content: "";
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: linear-gradient(90deg, #ff3ea5, #8b5cf6 55%, #16d9ff);
    }
    #channel-coach-app #cc-header-brand {
      flex: 1 1 auto !important;
      min-width: 0 !important;
      background: transparent !important;
      border: 0 !important;
      box-shadow: none !important;
    }
    #channel-coach-app .cc-brand-lockup {
      display: flex;
      align-items: center;
      gap: 14px;
      min-width: 0;
    }
    #channel-coach-app .cc-brand-icon {
      width: 52px;
      height: 52px;
      flex: 0 0 52px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 14px;
      color: #fff;
      background: linear-gradient(135deg, #ff3ea5, #8b5cf6);
      box-shadow: 0 0 20px rgba(255,62,165,.22);
    }
    #channel-coach-app .cc-brand-icon svg { width: 31px; height: 31px; }
    #channel-coach-app .cc-brand-copy { min-width: 0; }
    #channel-coach-app .cc-brand-name {
      color: #fff;
      font-size: 1.45rem;
      font-weight: 900;
      line-height: 1.2;
      letter-spacing: .035em;
      white-space: nowrap;
    }
    #channel-coach-app .cc-brand-name span { color: #ff3ea5; }
    #channel-coach-app .cc-brand-tagline {
      margin-top: 4px;
      color: #a6adc0;
      font-size: .72rem;
      font-weight: 700;
      letter-spacing: .15em;
      white-space: nowrap;
    }
    @media (max-width: 600px) {
      #channel-coach-app .cc-brand-lockup { gap: 8px; }
      #channel-coach-app .cc-brand-icon { width: 36px; height: 36px; flex-basis: 36px; border-radius: 10px; }
      #channel-coach-app .cc-brand-icon svg { width: 24px; height: 24px; }
      #channel-coach-app .cc-brand-name { font-size: .92rem; letter-spacing: 0; }
      #channel-coach-app .cc-brand-tagline { font-size: .52rem; letter-spacing: .035em; }
    }

    /* Dashboard layout containers: remove only the redundant outer frames.
       Keep the borders on the actual scheduled item, health and task cards. */
    #channel-coach-app #dashboard-page,
    #channel-coach-app #dashboard-output,
    #channel-coach-app #dashboard-output .cc-dashboard-wrap,
    #channel-coach-app #dashboard-output .cc-dashboard-grid,
    #channel-coach-app #dashboard-output .cc-dashboard-two-col,
    #channel-coach-app #dashboard-output .cc-dashboard-full-stack {
      border: none !important;
      outline: none !important;
      box-shadow: none !important;
    }

    /* Remove the redundant frame on the Dashboard title banner. */
    #channel-coach-app #dashboard-page .cc-dashboard-page-header {
      border: none !important;
      box-shadow: none !important;
    }

    /* Match the Dashboard's layout background to the true-black page.
       Keep the title banner and individual cards dark navy. */
    #channel-coach-app #dashboard-page,
    #channel-coach-app #dashboard-output,
    #channel-coach-app #dashboard-output .cc-dashboard-wrap,
    #channel-coach-app #dashboard-output .cc-dashboard-grid,
    #channel-coach-app #dashboard-output .cc-dashboard-two-col,
    #channel-coach-app #dashboard-output .cc-dashboard-full-stack {
      background: #000000 !important;
      background-image: none !important;
    }


    /* Compact neon navigation: reduce empty vertical space without touching Dashboard. */
    #channel-coach-app #cc-top-header {
      min-height: 0 !important;
      padding: 8px 16px 11px !important;
      gap: 12px !important;
      align-items: center !important;
    }
    #channel-coach-app #cc-top-header::after { height: 2px; }
    #channel-coach-app #cc-header-brand {
      min-height: 0 !important;
      align-self: center !important;
    }
    #channel-coach-app #cc-header-brand .html-container,
    #channel-coach-app #cc-header-brand .prose {
      padding: 0 !important;
      margin: 0 !important;
      min-height: 0 !important;
    }
    #channel-coach-app .cc-brand-lockup { gap: 11px; }
    #channel-coach-app .cc-brand-icon {
      width: 42px;
      height: 42px;
      flex-basis: 42px;
      border-radius: 12px;
    }
    #channel-coach-app .cc-brand-icon svg { width: 26px; height: 26px; }
    #channel-coach-app .cc-brand-name { font-size: 1.25rem; line-height: 1.12; }
    #channel-coach-app .cc-brand-tagline {
      margin-top: 2px;
      font-size: .62rem;
      letter-spacing: .12em;
    }
    #channel-coach-app #credit-balance { padding: 7px 13px !important; }
    #channel-coach-app #cc-header-menu {
      height: 40px !important;
      min-height: 40px !important;
      width: 44px !important;
      min-width: 44px !important;
      flex-basis: 44px !important;
    }
    @media (max-width: 600px) {
      #channel-coach-app #cc-top-header { padding: 8px 10px 10px !important; gap: 7px !important; }
      #channel-coach-app .cc-brand-icon { width: 34px; height: 34px; flex-basis: 34px; }
      #channel-coach-app .cc-brand-icon svg { width: 22px; height: 22px; }
      #channel-coach-app .cc-brand-name { font-size: .9rem; }
      #channel-coach-app .cc-brand-tagline { font-size: .5rem; letter-spacing: .025em; }
      #channel-coach-app #credit-balance { padding: 6px 8px !important; }
      #channel-coach-app #cc-header-menu {
        width: 38px !important;
        min-width: 38px !important;
        flex-basis: 38px !important;
        height: 36px !important;
        min-height: 36px !important;
      }
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
        with gr.Row(elem_id="cc-top-header"):
            gr.HTML(
                """<div class="cc-brand-lockup">
                    <div class="cc-brand-icon" aria-hidden="true">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M6.5 8h11a4 4 0 0 1 3.9 3.1l1 5.2a2 2 0 0 1-3.1 2l-3.2-2.4H7.9l-3.2 2.4a2 2 0 0 1-3.1-2l1-5.2A4 4 0 0 1 6.5 8Z"/>
                        <path d="M7 11v4m-2-2h4"/><circle cx="16" cy="11.5" r=".75" fill="currentColor" stroke="none"/><circle cx="18.5" cy="14" r=".75" fill="currentColor" stroke="none"/>
                      </svg>
                    </div>
                    <div class="cc-brand-copy">
                      <div class="cc-brand-name">CHANNEL <span>COACH</span></div>
                      <div class="cc-brand-tagline">CREATE · LEVEL UP · GROW</div>
                    </div>
                  </div>""",
                elem_id="cc-header-brand",
            )
            credit_balance = gr.Markdown("**Credits: —**", elem_id="credit-balance")
            menu_button = gr.Button("☰", elem_id="cc-header-menu", scale=0, min_width=52)

        with gr.Column(visible=False, elem_id="channel-coach-menu") as menu_panel:
            home_nav = gr.Button("\U0001F3E0 Home")
            chat_nav = gr.Button("\U0001F4AC Coach Chat")
            calendar_nav = gr.Button("\U0001F4C5 Calendar")
            toolkit_nav = gr.Button("\U0001F3AC Toolkit")
            settings_nav = gr.Button("\u2699\uFE0F Settings")
            bug_report_nav = gr.Button("\U0001F41E Report a Bug")
            bug_admin_nav = gr.Button("\U0001F6E0\uFE0F Bug Dashboard", visible=False)
            logout_button = gr.Button("\u21AA\uFE0F Log Out")

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

            workspace_button = gr.Button("\U0001F504 Load Workspace")

        # Coach Chat is available from the menu.
        # Creator Dashboard remains the logged-in home screen.
        chat_page = build_chat_page(
            workspace_name,
            credit_balance,
            visible=False,
        )

        (
            dashboard_page,
            dashboard_output,
            dashboard_open_calendar_button,
        ) = build_dashboard_page(
            workspace_name,
            visible=True,
        )

        def load_credit_balance(current_workspace):
            """Grant the one-time starter balance and show the current total."""
            if not current_workspace:
                return "**Credits: \u2014**"
            try:
                ensure_initial_credits(current_workspace)
                balance = get_credit_balance(current_workspace)
                return f"**Credits: {balance}**"
            except Exception as exc:
                print(f"Credit balance load failed: {exc}")
                gr.Warning("Credits are temporarily unavailable. Please try again shortly.")
                return "**Credits: unavailable**"

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
                )

            safe_workspace = current_workspace
            profile = load_creator_profile(safe_workspace)
            return (
                f"Current workspace: **{safe_workspace}**",
                render_creator_dashboard(safe_workspace),
                render_content_calendar(user_id=safe_workspace),
                render_upcoming_content(user_id=safe_workspace),
                gr.update(choices=get_calendar_choices(safe_workspace)),
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
            cc_calendar_selected_date,
        ) = build_calendar_page(
            workspace_name,
            visible=False,
        )

        toolkit_page = build_toolkit_page(
            workspace_name,
            visible=False,
        )

        settings_components = build_settings_page(
            workspace_name,
            dashboard_output,
            visible=False,
        )

        bug_report_page = build_bug_report_page(
            workspace_name,
            visible=False,
        )

        bug_admin_page = build_bug_admin_page(
            saved_login,
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
    PAGE_NAMES = ["chat", "dashboard", "calendar", "toolkit", "settings", "bugs", "bug_admin"]

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
        settings_page,
        bug_report_page,
        bug_admin_page,
        menu_panel,
        menu_open,
        current_page,
        previous_page,
    ]

    def open_next_creator_task(current):
        """Native Home-screen button: open the Content Calendar."""
        return navigate_to("calendar", current)

    dashboard_open_calendar_button.click(
        open_next_creator_task,
        inputs=[current_page],
        outputs=page_outputs,
        show_progress="hidden",
    )


    def open_calendar_from_dashboard(current, evt: gr.EventData):
        """Open the exact calendar date for the Creator Task clicked on Home."""
        selected_date = getattr(evt, "date", "") or ""
        nav = navigate_to("calendar", current)
        return (*nav, selected_date)

    # dashboard.py emits this submit event only when an actual
    # .cc-dashboard-task-link card is clicked.
    dashboard_output.submit(
        open_calendar_from_dashboard,
        inputs=[current_page],
        outputs=[*page_outputs, cc_calendar_selected_date],
        show_progress="hidden",
    )

    menu_button.click(
        toggle_menu,
        inputs=[menu_open],
        outputs=[menu_open, menu_panel],
        show_progress="hidden",
    )

    def open_home_and_refresh_dashboard(current, current_workspace):
        """Open Home and re-render the dashboard from the latest saved data."""
        nav = navigate_to("dashboard", current)
        fresh_dashboard = render_creator_dashboard(current_workspace) if current_workspace else gr.update()
        return (*nav, fresh_dashboard)

    home_nav.click(
        open_home_and_refresh_dashboard,
        inputs=[current_page, workspace_name],
        outputs=[*page_outputs, dashboard_output],
        show_progress="hidden",
    )

    # Calendar Save Progress refreshes cc_calendar_output.
    # Re-render Home immediately from the newly saved Supabase status.
    cc_calendar_output.change(
        lambda current_workspace: (
            render_creator_dashboard(current_workspace)
            if current_workspace
            else gr.update()
        ),
        inputs=[workspace_name],
        outputs=[dashboard_output],
        show_progress="hidden",
    )
    chat_nav.click(
        lambda current: navigate_to("chat", current),
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
    settings_nav.click(
        lambda current: navigate_to("settings", current),
        inputs=[current_page],
        outputs=page_outputs,
        show_progress="hidden",
    )
    bug_report_nav.click(
        lambda current: navigate_to("bugs", current),
        inputs=[current_page],
        outputs=page_outputs,
        show_progress="hidden",
    )
    bug_admin_nav.click(
        lambda current: navigate_to("bug_admin", current),
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
    ).then(
        load_credit_balance,
        inputs=[workspace_name],
        outputs=[credit_balance],
        show_progress="hidden",
    ).then(
        admin_button_visibility,
        inputs=[saved_login],
        outputs=[bug_admin_nav],
        show_progress="hidden",
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
    ).then(
        load_credit_balance,
        inputs=[workspace_name],
        outputs=[credit_balance],
        show_progress="hidden",
    ).then(
        admin_button_visibility,
        inputs=[saved_login],
        outputs=[bug_admin_nav],
        show_progress="hidden",
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





    
 
        
 
      
 
      
    
 
      
    
 
      


    
 
      
 
      
    
 
      
      
    
 
      
    
 
      













    
 
        
 
      
 
      
    
 
      
    
 
      


    
 
      
 
      
    
 
      
      
    
 
      
    
 
      
