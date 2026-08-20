import gradio as gr


def _respond(message, history):
    """
    Safe placeholder response handler.
    Replace the reply logic here with your real Channel Coach backend.
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
    Full-page Coach Chat interface.

    Fixes:
    - Removes the unsupported `type=` argument from gr.Chatbot.
    - Prevents Gradio Textbox objects from being rendered inside Markdown/text.
    - Keeps the chat layout simple and ChatGPT-like.
    """

    with gr.Column(
        visible=visible,
        elem_id="coach-chat-page",
    ) as chat_page:

        gr.Markdown(
            "## Coach Chat",
            elem_id="coach-chat-heading",
        )

        chatbot = gr.Chatbot(
            value=[],
            height=560,
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

    # Optional references for app.py if needed.
    chat_page.chatbot = chatbot
    chat_page.message_box = message_box
    chat_page.send_button = send_button
    chat_page.clear_button = clear_button

    return chat_page


    
