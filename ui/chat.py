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
    Backend is unchanged; this version only cleans up the visual styling.
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
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        margin-bottom: 8px !important;
    }

    .cc-chat-title {
        font-weight: 800;
        letter-spacing: .04em;
    }

    .cc-chat-orb {
        color: #a855f7;
        margin-right: 7px;
    }

    /* Remove Gradio's big gray Chatbot panel */
    #coach-chatbot,
    #coach-chatbot > div,
    #coach-chatbot .wrap,
    #coach-chatbot .panel,
    #coach-chatbot .container,
    #coach-chatbot .bubble-wrap {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    #coach-chatbot {
        min-height: 58vh !important;
        padding: 10px 0 100px 0 !important;
    }

    /* Remove gray empty-state / internal panel styling */
    #coach-chatbot [class*="container"],
    #coach-chatbot [class*="panel"] {
        background: transparent !important;
        border-color: transparent !important;
        box-shadow: none !important;
    }

    /* Chat messages */
    #coach-chatbot .message {
        border-radius: 18px !important;
        border: 1px solid rgba(168, 85, 247, .24) !important;
        box-shadow: none !important;
    }

    /* Composer */
    #coach-chat-composer {
        position: sticky !important;
        bottom: 12px !important;
        z-index: 20 !important;
        width: min(900px, 96%) !important;
        margin: 0 auto !important;
        padding: 8px 10px !important;
        border: 1px solid rgba(168, 85, 247, .65) !important;
        border-radius: 24px !important;
        background: rgba(7, 7, 14, .97) !important;
        box-shadow:
            0 0 18px rgba(168, 85, 247, .12),
            0 8px 30px rgba(0, 0, 0, .28) !important;
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
        background: linear-gradient(135deg, #7c3aed, #c026d3) !important;
        border: none !important;
        box-shadow: 0 0 16px rgba(168, 85, 247, .35) !important;
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


    
