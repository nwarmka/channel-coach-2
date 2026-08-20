import gradio as gr


def _respond(message, history):
    """
    Temporary safe chat handler.

    This keeps the UI working even before your real Channel Coach
    response function is wired back in.
    """
    message = (message or "").strip()
    history = history or []

    if not message:
        return "", history

    # Gradio-compatible tuple history format.
    reply = (
        "Coach Chat is connected and the page is working. "
        "Your full coaching response logic can be wired into _respond()."
    )
    history = history + [(message, reply)]
    return "", history


def build_chat_page(workspace_name="Channel Coach", visible=False):
    """
    Build the full-page Channel Coach chat interface.

    Important compatibility fix:
    - Does NOT pass type='messages' to gr.Chatbot().
      That argument is what caused the Render crash:
      TypeError: Chatbot.__init__() got an unexpected keyword argument 'type'
    """

    css = """
    .channel-coach-chat {
        min-height: 78vh;
    }

    .channel-coach-title {
        text-align: center;
        margin-bottom: 0.25rem;
    }

    .channel-coach-subtitle {
        text-align: center;
        opacity: 0.75;
        margin-bottom: 1rem;
    }

    #channel-coach-chatbot {
        min-height: 560px;
    }
    """

    with gr.Column(
        visible=visible,
        elem_classes=["channel-coach-chat"],
    ) as chat_page:
        gr.Markdown(
            f"# {workspace_name}",
            elem_classes=["channel-coach-title"],
        )

        chatbot = gr.Chatbot(
            value=[],
            height=560,
            elem_id="channel-coach-chatbot",
        )

        with gr.Row():
            message_box = gr.Textbox(
                placeholder="Message Channel Coach...",
                show_label=False,
                lines=1,
                scale=8,
            )
            send_button = gr.Button(
                "Send",
                variant="primary",
                scale=1,
            )

        clear_button = gr.Button("Clear chat")

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

    # Expose useful components in case app.py needs them later.
    chat_page.chatbot = chatbot
    chat_page.message_box = message_box
    chat_page.send_button = send_button
    chat_page.clear_button = clear_button
    chat_page.custom_css = css

    return chat_page

    
