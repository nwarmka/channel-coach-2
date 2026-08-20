import gradio as gr

# Use the real Channel Coach backend that already exists in features.py
from features import ask_creator_coach


def _respond(message, history, workspace_name):
    """
    Send a Coach Chat message using the creator's actual workspace data.

    Uses Gradio's messages format:
    {"role": "user", "content": "..."}
    {"role": "assistant", "content": "..."}
    """
    message = (message or "").strip()
    history = history or []

    if not message:
        return "", history

    # workspace_name is a Gradio component value passed in from app.py.
    user_id = (workspace_name or "main").strip() or "main"

    # Real Channel Coach response from features.py
    reply = ask_creator_coach(message, user_id=user_id)

    history = history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": reply},
    ]

    return "", history


def build_chat_page(workspace_name, visible=False):
    """
    Full-page Channel Coach chat connected to the real Coach Chat backend.
    """

    with gr.Column(
        visible=visible,
        elem_id="chat-page",
    ) as chat_page:

        # This matches the CSS already defined in app.py.
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


    
