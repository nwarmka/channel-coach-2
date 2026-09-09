import gradio as gr

# Keep the real, working Channel Coach backend.
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
    """
    Full-page Coach Chat.
    Backend is unchanged; this version gives the conversation area
    a visibly distinct cyberpunk panel.
    """

    css = """
    /* Main Coach Chat page */
    #chat-page {
        min-height: 82vh !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    #coach-chat-header {
        background: rgba(18, 20, 40, .92) !important;
        border: 1px solid rgba(168, 85, 247, .55) !important;
        border-radius: 18px !important;
        box-shadow: 0 0 22px rgba(168, 85, 247, .10) !important;
        margin: 0 auto 14px !important;
        padding: 12px 16px !important;
        width: min(900px, 96%) !important;
    }

    .cc-chat-title {
        font-weight: 800;
        letter-spacing: .04em;
        color: #f7f7ff;
    }

    .cc-chat-orb {
        color: #22d3ee;
        margin-right: 7px;
        text-shadow: 0 0 10px rgba(34, 211, 238, .55);
    }

    /* Distinct conversation surface */
    #coach-chatbot {
        min-height: 58vh !important;
        width: min(900px, 96%) !important;
        margin: 0 auto !important;
        padding: 14px 14px 105px 14px !important;

        background:
            radial-gradient(circle at 16% 0%, rgba(139, 92, 246, .30), transparent 36%),
            radial-gradient(circle at 90% 12%, rgba(34, 211, 238, .10), transparent 30%),
            linear-gradient(180deg, #252b4d 0%, #1e2442 55%, #181d35 100%) !important;

        border: 2px solid rgba(168, 85, 247, .82) !important;
        border-radius: 22px !important;

        box-shadow:
            inset 0 0 34px rgba(139, 92, 246, .10),
            0 18px 40px rgba(0, 0, 0, .35),
            0 0 30px rgba(139, 92, 246, .16) !important;
    }

    /* Override Gradio's internal transparent/gray wrappers */
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

    /* Base chat message style */
    #coach-chatbot .message {
        border-radius: 18px !important;
        line-height: 1.55 !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, .18) !important;
    }

    /* User messages */
    #coach-chatbot .message.user,
    #coach-chatbot [data-testid="user"] {
        background: linear-gradient(
            135deg,
            rgba(124, 58, 237, .82),
            rgba(192, 38, 211, .66)
        ) !important;
        border: 1px solid rgba(244, 114, 182, .62) !important;
        color: white !important;
    }

    /* Coach messages */
    #coach-chatbot .message.bot,
    #coach-chatbot .message.assistant,
    #coach-chatbot [data-testid="bot"] {
        background: linear-gradient(
            135deg,
            #343c67,
            #2a3158
        ) !important;
        border: 1px solid rgba(34, 211, 238, .30) !important;
        color: #f7f8ff !important;
    }

    /* Composer */
    #coach-chat-composer {
        position: sticky !important;
        bottom: 12px !important;
        z-index: 20 !important;
        width: min(900px, 96%) !important;
        margin: 0 auto !important;
        padding: 8px 10px !important;
        border: 1px solid rgba(168, 85, 247, .72) !important;
        border-radius: 24px !important;
        background: rgba(12, 14, 28, .98) !important;
        box-shadow:
            0 0 20px rgba(168, 85, 247, .16),
            0 8px 30px rgba(0, 0, 0, .30) !important;
        align-items: center !important;
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
        font-size: 16px !important;
        padding: 10px 8px !important;
    }

    #coach-chat-input textarea:focus {
        outline: none !important;
        box-shadow: none !important;
    }

    #coach-chat-send {
        border-radius: 50% !important;
        min-width: 46px !important;
        width: 46px !important;
        height: 46px !important;
        padding: 0 !important;
        font-size: 20px !important;
        background: linear-gradient(135deg, #7c3aed, #ec4899) !important;
        border: none !important;
        box-shadow: 0 0 18px rgba(236, 72, 153, .38) !important;
    }

    @media (max-width: 700px) {
        #coach-chat-header,
        #coach-chatbot,
        #coach-chat-composer {
            width: 100% !important;
        }

        #coach-chatbot {
            min-height: 56vh !important;
            padding-left: 10px !important;
            padding-right: 10px !important;
        }
    }
    """

    with gr.Column(visible=visible, elem_id="chat-page") as chat_page:
        gr.HTML(f"<style>{css}</style>")

        with gr.Row(elem_id="coach-chat-header"):
            gr.HTML(
                """
                <div class="cc-chat-title">
                    <span class="cc-chat-orb">✦</span>
                    COACH CHAT
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
                placeholder="Message Channel Coach...",
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


    
