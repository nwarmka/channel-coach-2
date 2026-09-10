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


def build_chat_page(workspace_name, credit_balance=None, visible=False):
    """
    Full-page Coach Chat using Gradio's panel layout.
    Keeps the Channel Coach styling while avoiding the nested
    chat-bubble look.
    """

    css = """
    #chat-page {
        min-height: 78vh !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding-top: 0 !important;
    }

    /* =========================
       HEADER
       ========================= */

    #coach-chat-header {
        width: min(900px, 96%) !important;
        margin: 0 auto 26px !important;
        padding: 10px 14px !important;

        border-radius: 16px !important;
        background: rgba(14, 18, 34, .94) !important;
        border: 1px solid rgba(168, 85, 247, .45) !important;

        box-shadow:
            0 0 16px rgba(168, 85, 247, .08) !important;

        align-items: center !important;
    }

    .cc-chat-header-inner {
        display: flex;
        align-items: center;
        gap: 9px;
        width: 100%;
    }

    .cc-chat-orb {
        color: #22d3ee;
        font-size: 15px;
        text-shadow:
            0 0 10px rgba(34, 211, 238, .55);
    }

    .cc-chat-title {
        color: #f7f7ff;
        font-size: .92rem;
        font-weight: 800;
        letter-spacing: .04em;
    }

    /* =========================
       CHAT WINDOW
       ========================= */

    #coach-chatbot {
        width: min(900px, 96%) !important;

        min-height: 320px !important;
        height: 320px !important;

        margin: 0 auto 26px !important;

        background:
            radial-gradient(
                circle at 18% 0%,
                rgba(139, 92, 246, .10),
                transparent 34%
            ),
            linear-gradient(
                180deg,
                #0b1020 0%,
                #080d18 100%
            ) !important;

        border:
            2px solid rgba(168, 85, 247, .82) !important;

        border-radius: 22px !important;

        box-shadow:
            inset 0 0 28px rgba(139, 92, 246, .05),
            0 12px 28px rgba(0, 0, 0, .24) !important;

        overflow: hidden !important;
    }

    /*
       Remove Gradio's outer component chrome,
       but leave the panel message layout alone.
    */
    #coach-chatbot > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    #coach-chatbot label,
    #coach-chatbot .label-wrap {
        display: none !important;
    }

    /*
       Make text readable and keep the panel clean.
    */
    #coach-chatbot .message {
        line-height: 1.65 !important;
    }

    #coach-chatbot .message p {
        margin-top: 0 !important;
        margin-bottom: 14px !important;
    }

    #coach-chatbot .message p:last-child {
        margin-bottom: 0 !important;
    }

    /* =========================
       USER MESSAGE
       ========================= */

    /*
       Keep your own messages visually distinct.
    */
    #coach-chatbot [data-testid="user"] {
        background:
            linear-gradient(
                135deg,
                rgba(124, 58, 237, .86),
                rgba(190, 24, 93, .68)
            ) !important;

        border:
            1px solid rgba(244, 114, 182, .48) !important;

        border-radius: 14px !important;

        color: white !important;
    }

    /* =========================
       ASSISTANT MESSAGE
       ========================= */

    /*
       Coach responses should read more like
       full-width content inside the panel.
    */
    #coach-chatbot [data-testid="assistant"],
    #coach-chatbot [data-testid="bot"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #f8fafc !important;
    }

    /* =========================
       ACTION BUTTONS
       ========================= */

    #coach-chatbot button {
        background: rgba(10, 13, 26, .72) !important;
        border:
            1px solid rgba(148, 163, 184, .24) !important;
        border-radius: 7px !important;
    }

    /* =========================
       COMPOSER
       ========================= */

    #coach-chat-composer {
        width: min(900px, 96%) !important;

        margin: 0 auto !important;

        padding: 7px 8px 7px 12px !important;

        border-radius: 18px !important;

        background:
            rgba(10, 13, 26, .98) !important;

        border:
            1px solid rgba(168, 85, 247, .55) !important;

        box-shadow:
            0 8px 22px rgba(0, 0, 0, .24) !important;

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

        font-size: 15px !important;

        padding: 9px 7px !important;
    }

    #coach-chat-input textarea::placeholder {
        color: rgba(226, 232, 240, .48) !important;
    }

    #coach-chat-input textarea:focus {
        outline: none !important;
        box-shadow: none !important;
    }

    /* =========================
       SEND BUTTON
       ========================= */

    #coach-chat-send {
        min-width: 42px !important;
        width: 42px !important;
        height: 42px !important;

        padding: 0 !important;

        border-radius: 13px !important;

        font-size: 17px !important;

        color: white !important;

        background:
            linear-gradient(
                135deg,
                #7c3aed,
                #ec4899
            ) !important;

        border: none !important;

        box-shadow:
            0 0 15px rgba(236, 72, 153, .28) !important;
    }

    #coach-chat-send:hover {
        transform: translateY(-1px) !important;
    }

    /* =========================
       MOBILE
       ========================= */

    @media (max-width: 700px) {
        #coach-chat-header,
        #coach-chatbot,
        #coach-chat-composer {
            width: 100% !important;
        }

        #coach-chatbot {
            min-height: 54vh !important;
            height: 54vh !important;
        }
    }
    """

    with gr.Column(
        visible=visible,
        elem_id="chat-page"
    ) as chat_page:

        gr.HTML(f"<style>{css}</style>")

        with gr.Row(elem_id="coach-chat-header"):
            gr.HTML(
                """
                <div class="cc-chat-header-inner">
                    <span class="cc-chat-orb">✦</span>
                    <span class="cc-chat-title">COACH CHAT</span>
                </div>
                """
            )

        chatbot = gr.Chatbot(
            value=[],
            elem_id="coach-chatbot",
            label=None,
            layout="panel",
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
            inputs=[
                message_box,
                chatbot,
                workspace_name,
            ],
            outputs=[
                message_box,
                chatbot,
            ],
        )

        message_box.submit(
            fn=_respond,
            inputs=[
                message_box,
                chatbot,
                workspace_name,
            ],
            outputs=[
                message_box,
                chatbot,
            ],
        )

    return chat_page


    
