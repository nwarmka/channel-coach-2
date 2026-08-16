# Channel Coach - Coach Chat UI

import gradio as gr

from features import ask_creator_coach


def build_chat_page(workspace_name, visible=False):
    """Build the main Channel Coach Chat page and wire its events."""

    with gr.Column(
        visible=visible,
        elem_id="chat-page",
    ) as chat_page:

        gr.Markdown("## 💬 Channel Coach Chat")

        gr.Markdown(
            "Ask Channel Coach what to work on next, "
            "what to improve, or how to grow your channel."
        )

        chat_question = gr.Textbox(
            label="Ask Channel Coach",
            placeholder="What should I work on today?",
            lines=3,
        )

        chat_button = gr.Button(
            "Send",
            variant="primary",
        )

        chat_output = gr.Markdown()

        chat_button.click(
            ask_creator_coach,
            inputs=[
                chat_question,
                workspace_name,
            ],
            outputs=chat_output,
            show_progress="full",
        )

    return chat_page

