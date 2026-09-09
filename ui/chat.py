import gradio as gr

from features import ask_creator_coach


def _respond(message, history, workspace_name):
    message = (message or "").strip()
    history = history or []

    if not message:
        return "", history

    user_id = (workspace_name or "main").strip() or "main"
    reply = ask_creator_coach(message, user_id=user_id)

    history = history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": reply},
    ]

    return "", history


def build_chat_page(workspace_name, visible=False):
    css = """
    #chat-page {
        min-height: 82vh !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding-top: 2px !important;
    }

    #coach-chat-header {
        position: relative !important;
        overflow: hidden !important;
        background: linear-gradient(135deg, rgba(23,24,48,.96), rgba(13,18,35,.96)) !important;
        border: 1px solid rgba(168,85,247,.58) !important;
        border-radius: 18px !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,.03), 0 0 24px rgba(168,85,247,.10) !important;
        margin: 0 auto 10px !important;
        padding: 13px 16px !important;
        width: min(980px, 96%) !important;
        align-items: center !important;
    }

    #coach-chat-header::after {
        content: "" !important;
        position: absolute !important;
        left: 0 !important;
        right: 0 !important;
        bottom: 0 !important;
        height: 2px !important;
        background: linear-gradient(90deg, transparent, #22d3ee 18%, #8b5cf6 50%, #ec4899 82%, transparent) !important;
        opacity: .85 !important;
    }

    .cc-chat-header-inner {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 14px;
        width: 100%;
    }

    .cc-chat-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        min-width: 0;
    }

    .cc-chat-icon {
        width: 40px;
        height: 40px;
        flex: 0 0 40px;
        display: grid;
        place-items: center;
        border-radius: 12px;
        color: #ecfeff;
        font-size: 18px;
        background: radial-gradient(circle at 30% 25%, rgba(34,211,238,.38), transparent 45%), linear-gradient(135deg, rgba(124,58,237,.85), rgba(30,41,59,.92));
        border: 1px solid rgba(34,211,238,.38);
        box-shadow: inset 0 0 18px rgba(34,211,238,.08), 0 0 18px rgba(139,92,246,.22);
    }

    .cc-chat-copy { min-width: 0; }

    .cc-chat-title {
        margin: 0;
        font-size: .98rem;
        font-weight: 850;
        letter-spacing: .055em;
        color: #f8f7ff;
    }

    .cc-chat-subtitle {
        margin-top: 2px;
        font-size: .77rem;
        color: rgba(226,232,240,.66);
        letter-spacing: .015em;
    }

    .cc-chat-status {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        flex: 0 0 auto;
        padding: 6px 9px;
        border-radius: 999px;
        font-size: .69rem;
        font-weight: 800;
        letter-spacing: .08em;
        color: #a7f3d0;
        background: rgba(16,185,129,.08);
        border: 1px solid rgba(16,185,129,.24);
    }

    .cc-chat-status-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #34d399;
        box-shadow: 0 0 10px rgba(52,211,153,.8);
    }

    #coach-chatbot {
        min-height: 60vh !important;
        width: min(980px, 96%) !important;
        margin: 0 auto !important;
        padding: 18px 18px 108px 18px !important;
        background:
            linear-gradient(rgba(255,255,255,.018) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,.018) 1px, transparent 1px),
            radial-gradient(circle at 12% 0%, rgba(139,92,246,.28), transparent 34%),
            radial-gradient(circle at 92% 6%, rgba(34,211,238,.11), transparent 28%),
            linear-gradient(180deg, #222947 0%, #1a213a 52%, #141a2e 100%) !important;
        background-size: 28px 28px, 28px 28px, auto, auto, auto !important;
        border: 1px solid rgba(168,85,247,.72) !important;
        border-radius: 22px !important;
        box-shadow: inset 0 0 46px rgba(139,92,246,.08), 0 18px 42px rgba(0,0,0,.32), 0 0 28px rgba(139,92,246,.13) !important;
    }

    #coach-chatbot > div,
    #coach-chatbot .wrap,
    #coach-chatbot .panel,
    #coach-chatbot .container,
    #coach-chatbot .bubble-wrap,
    #coach-chatbot [class*="container"],
    #coach-chatbot [class*="panel"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    #coach-chatbot .message {
        max-width: 78% !important;
        border-radius: 18px !important;
        line-height: 1.55 !important;
        padding: 11px 14px !important;
        box-shadow: 0 8px 20px rgba(0,0,0,.18) !important;
        backdrop-filter: blur(8px) !important;
    }

    #coach-chatbot .message.user,
    #coach-chatbot [data-testid="user"] {
        background: linear-gradient(135deg, rgba(124,58,237,.88), rgba(192,38,211,.72)) !important;
        border: 1px solid rgba(244,114,182,.58) !important;
        color: white !important;
    }

    #coach-chatbot .message.bot,
    #coach-chatbot .message.assistant,
    #coach-chatbot [data-testid="bot"] {
        background: linear-gradient(135deg, rgba(51,65,104,.95), rgba(36,47,81,.96)) !important;
        border: 1px solid rgba(34,211,238,.28) !important;
        color: #f8fbff !important;
    }

    #coach-chat-composer {
        position: sticky !important;
        bottom: 12px !important;
        z-index: 20 !important;
        width: min(940px, 92%) !important;
        margin: -68px auto 16px !important;
        padding: 8px 9px 8px 14px !important;
        border: 1px solid rgba(168,85,247,.66) !important;
        border-radius: 22px !important;
        background: linear-gradient(180deg, rgba(14,17,33,.985), rgba(9,12,24,.985)) !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,.025), 0 0 22px rgba(168,85,247,.15), 0 12px 30px rgba(0,0,0,.34) !important;
        align-items: center !important;
        backdrop-filter: blur(16px) !important;
    }

    #coach-chat-input,
    #coach-chat-input > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    #coach-chat-input textarea {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: white !important;
        font-size: 15px !important;
        padding: 10px 8px !important;
    }

    #coach-chat-input textarea::placeholder {
        color: rgba(226,232,240,.50) !important;
    }

    #coach-chat-send {
        border-radius: 14px !important;
        min-width: 44px !important;
        width: 44px !important;
        height: 44px !important;
        padding: 0 !important;
        font-size: 18px !important;
        color: white !important;
        background: linear-gradient(135deg, #7c3aed 0%, #a855f7 46%, #ec4899 100%) !important;
        border: 1px solid rgba(255,255,255,.08) !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,.14), 0 0 18px rgba(236,72,153,.32) !important;
    }

    @media (max-width: 700px) {
        #coach-chat-header,
        #coach-chatbot {
            width: 100% !important;
        }

        #coach-chat-composer {
            width: calc(100% - 18px) !important;
        }

        .cc-chat-subtitle {
            display: none;
        }

        #coach-chatbot {
            min-height: 58vh !important;
            padding-left: 10px !important;
            padding-right: 10px !important;
        }

        #coach-chatbot .message {
            max-width: 88% !important;
        }
    }
    """

    with gr.Column(visible=visible, elem_id="chat-page") as chat_page:
        gr.HTML(f"<style>{css}</style>")

        with gr.Row(elem_id="coach-chat-header"):
            gr.HTML(
                """
                <div class="cc-chat-header-inner">
                    <div class="cc-chat-brand">
                        <div class="cc-chat-icon">✦</div>
                        <div class="cc-chat-copy">
                            <div class="cc-chat-title">COACH CHAT</div>
                            <div class="cc-chat-subtitle">Strategy · Planning · Feedback</div>
                        </div>
                    </div>
                    <div class="cc-chat-status">
                        <span class="cc-chat-status-dot"></span>
                        READY
                    </div>
                </div>
                """
            )

        chatbot = gr.Chatbot(
            value=[],
            elem_id="coach-chatbot",
            label=None,
        )

        with gr.Row(elem_id="coach-chat-composer"):
            message_box = gr.Textbox(
                value="",
                placeholder="Ask Channel Coach anything...",
                show_label=False,
                lines=1,
                max_lines=6,
                scale=12,
                container=False,
                elem_id="coach-chat-input",
            )

            send_button = gr.Button(
                "➤",
                variant="primary",
                scale=0,
                min_width=48,
                elem_id="coach-chat-send",
            )

        send_button.click(
            fn=_respond,
            inputs=[message_box, chatbot, workspace_name],
            outputs=[message_box, chatbot],
        )

        message_box.submit(
            fn=_respond,
            inputs=[message_box, chatbot, workspace_name],
            outputs=[message_box, chatbot],
        )

    return chat_page



    
