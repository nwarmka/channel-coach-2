# Channel Coach - Full Page Coach Chat UI

import gradio as gr

from features import ask_creator_coach


def _send_chat_message(message, history, workspace_name):
    """
    Send a user message to Channel Coach and append both sides
    of the conversation to the visible chat history.
    """
    message = (message or "").strip()

    if not message:
        return history, ""

    history = history or []

    # Show the user's message.
    history.append(
        {
            "role": "user",
            "content": message,
        }
    )

    try:
        response = ask_creator_coach(
            message,
            workspace_name,
        )

        if not response:
            response = (
                "I couldn't generate a response. "
                "Please try again."
            )

    except Exception as exc:
        response = (
            "Something went wrong while generating "
            f"the response: {exc}"
        )

    # Show Channel Coach's response.
    history.append(
        {
            "role": "assistant",
            "content": response,
        }
    )

    # Return updated conversation + clear input.
    return history, ""


def build_chat_page(workspace_name, visible=False):
    """
    Build the full-page Channel Coach conversation interface.
    """

    with gr.Column(
        visible=visible,
        elem_id="chat-page",
    ) as chat_page:

        # Minimal header — no starter cards/prompts.
        with gr.Row(elem_id="coach-chat-header"):
            gr.Markdown(
                """
                <div class="cc-chat-title">
                    <span class="cc-chat-orb">✦</span>
                    <span>COACH CHAT</span>
                </div>
                """
            )

        # Conversation fills the page.
        chatbot = gr.Chatbot(
            value=[],
            type="messages",
            show_label=False,
            elem_id="coach-chatbot",
            height=560,
        )

        # Bottom composer, similar to ChatGPT.
        with gr.Row(
            elem_id="coach-chat-composer",
            equal_height=True,
        ):
            chat_question = gr.Textbox(
                placeholder="Message Channel Coach...",
                show_label=False,
                lines=1,
                max_lines=6,
                container=False,
                scale=12,
                elem_id="coach-chat-input",
            )

            chat_button = gr.Button(
                "➤",
                variant="primary",
                scale=1,
                min_width=54,
                elem_id="coach-chat-send",
            )

        # Send button.
        chat_button.click(
            _send_chat_message,
            inputs=[
                chat_question,
                chatbot,
                workspace_name,
            ],
            outputs=[
                chatbot,
                chat_question,
            ],
            show_progress="minimal",
        )

        # Enter key sends too.
        chat_question.submit(
            _send_chat_message,
            inputs=[
                chat_question,
                chatbot,
                workspace_name,
            ],
            outputs=[
                chatbot,
                chat_question,
            ],
            show_progress="minimal",
        )

    return chat_page
    
