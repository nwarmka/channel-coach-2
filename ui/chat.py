import gradio as gr


def _respond(message, history):
    """
    Temporary response handler.
    Replace this with your real Channel Coach logic later.
    """
    message = (message or "").strip()
    history = history or []

    if not message:
        return "", history

    reply = (
        "Coach Chat is online. "
        "Your full Channel Coach response logic can be connected here."
    )

    history = history + [(message, reply)]
    return "", history


def build_chat_page(workspace_name="Channel Coach", visible=False):
    """
    ChatGPT-style full-page Coach Chat.

    Key UI changes:
    - No giant bordered chatbot panel
    - No fixed 560px box
    - Chat area blends into the page background
    - Input sits at the bottom in a rounded composer
    """

    css = """
    #coach-chat-page {
        min-height: 82vh;
        display: flex;
        flex-direction: column;
        background: transparent !important;
    }

    #coach-chat-heading {
        margin: 0 0 8px 0;
        padding: 0;
        border: none !important;
        background: transparent !important;
    }

    #coach-chatbot {
        flex: 1;
        min-height: 58vh;
        border: none !important;
        box-shadow: none !important;
        background: transparent !important;
        padding: 8px 0 90px 0 !important;
    }

    #coach-chatbot > div {
        border: none !important;
        box-shadow: none !important;
        background: transparent !important;
    }

    #coach-chatbot .wrap,
    #coach-chatbot .panel,
    #coach-chatbot .container {
        border: none !important;
        box-shadow: none !important;
        background: transparent !important;
    }

    #coach-input-row {
        position: sticky;
        bottom: 12px;
        z-index: 20;
        width: min(900px, 96%);
        margin: 0 auto;
        padding: 8px;
        border: 1px solid rgba(143, 94, 255, 0.55);
        border-radius: 22px;
        background: rgba(10, 10, 18, 0.96);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25);
        align-items: center;
    }

    #coach-message-box {
        border: none !important;
        box-shadow: none !important;
        background: transparent !important;
    }

    #coach-message-box textarea {
        border: none !important;
        box-shadow: none !important;
        background: transparent !important;
        color: white !important;
        font-size: 16px !important;
    }

    #coach-send-button {
        min-width: 88px !important;
        border-radius: 16px !important;
    }

    #coach-clear-button {
        width: fit-content;
        margin: 8px auto 0 auto;
        opacity: 0.7;
    }
    """

    with gr.Column(
        visible=visible,
        elem_id="coach-chat-page",
    ) as chat_page:

        gr.HTML(f"<style>{css}</style>")

        gr.Markdown(
            "## Coach Chat",
            elem_id="coach-chat-heading",
        )

        chatbot = gr.Chatbot(
            value=[],
            elem_id="coach-chatbot",
            label=None,
        )

        with gr.Row(elem_id="coach-input-row"):
            message_box = gr.Textbox(
                value="",
                placeholder="Message Channel Coach...",
                show_label=False,
                lines=1,
                max_lines=6,
                scale=9,
                container=False,
                elem_id="coach-message-box",
            )

            send_button = gr.Button(
                "Send",
                variant="primary",
                scale=1,
                elem_id="coach-send-button",
            )

        clear_button = gr.Button(
            "Clear chat",
            elem_id="coach-clear-button",
        )

        send_button.click(
            fn=_respond,
            inputs=[message_box, chatbot],
            outputs=[message_box, chatbot],
        )

        message_box.submit(
            fn=_respond,
            inputs=[message_box, chatbot],
            outputs=[message_box, chatbot],
        )

        clear_button.click(
            fn=lambda: ("", []),
            inputs=None,
            outputs=[message_box, chatbot],
        )

    chat_page.chatbot = chatbot
    chat_page.message_box = message_box
    chat_page.send_button = send_button
    chat_page.clear_button = clear_button

    return chat_page


    
