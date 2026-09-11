import html
import time

import gradio as gr

from features import stream_creator_coach


def _format_message(text):
    """
    Safely format message text for the custom chat display.
    """
    text = html.escape(str(text or ""))
    lines = text.split("\n")
    formatted = []

    for line in lines:
        stripped = line.strip()

        if not stripped:
            formatted.append("<div class='cc-space'></div>")
            continue

        if stripped.startswith("- "):
            formatted.append(
                f"<div class='cc-bullet'>• {stripped[2:]}</div>"
            )
        elif stripped.startswith("* "):
            formatted.append(
                f"<div class='cc-bullet'>• {stripped[2:]}</div>"
            )
        else:
            formatted.append(
                f"<div class='cc-line'>{stripped}</div>"
            )

    return "".join(formatted)


def _render_chat(history):
    """
    Render the conversation ourselves so there are no Gradio
    chatbot message boxes.
    """
    history = history or []

    if not history:
        return """
        <div class="cc-empty">
            Ask Channel Coach anything to get started.
        </div>
        """

    output = []

    for item in history:
        role = item.get("role", "")
        raw_content = item.get("content", "")
        content = _format_message(raw_content)

        if role == "user":
            output.append(
                f"""
                <div class="cc-message-row cc-user-row">
                    <div class="cc-user-message">
                        {content}
                    </div>
                </div>
                """
            )

        elif role == "assistant":
            is_thinking = bool(item.get("thinking"))

            if is_thinking:
                output.append(
                    """
                    <div class="cc-message-row cc-assistant-row">
                        <div class="cc-coach-label">
                            ✦ CHANNEL COACH
                        </div>

                        <div class="cc-thinking">
                            <span class="cc-thinking-dot"></span>
                            <span class="cc-thinking-dot"></span>
                            <span class="cc-thinking-dot"></span>
                            <span class="cc-thinking-text">
                                Channel Coach is thinking...
                            </span>
                        </div>
                    </div>
                    """
                )
            else:
                output.append(
                    f"""
                    <div class="cc-message-row cc-assistant-row">
                        <div class="cc-coach-label">
                            ✦ CHANNEL COACH
                        </div>

                        <div class="cc-assistant-message">
                            {content}
                        </div>
                    </div>
                    """
                )

    return "".join(output)


def _respond(message, history, workspace_name):
    """
    Generator callback.

    It immediately shows the user's message and a thinking indicator,
    then updates the assistant response live as OpenAI streams text.
    """
    message = (message or "").strip()
    history = list(history or [])

    if not message:
        yield "", history, _render_chat(history)
        return

    user_id = (workspace_name or "main").strip() or "main"

    # Show the user's message instantly.
    working_history = history + [
        {
            "role": "user",
            "content": message,
        },
        {
            "role": "assistant",
            "content": "",
            "thinking": True,
        },
    ]

    yield "", working_history, _render_chat(working_history)

    partial_reply = ""
    last_ui_update = 0.0

    try:
        for delta in stream_creator_coach(
            message,
            user_id=user_id,
        ):
            partial_reply += delta

            # Once the first text arrives, remove the thinking indicator.
            working_history[-1] = {
                "role": "assistant",
                "content": partial_reply,
                "thinking": False,
            }

            # Throttle UI redraws slightly so Gradio does not re-render
            # the full HTML tree for every tiny token fragment.
            now = time.monotonic()

            if now - last_ui_update >= 0.05:
                yield (
                    "",
                    working_history,
                    _render_chat(working_history),
                )
                last_ui_update = now

        # Guarantee the final complete response is rendered.
        working_history[-1] = {
            "role": "assistant",
            "content": partial_reply or "I couldn't generate a response.",
            "thinking": False,
        }

        yield (
            "",
            working_history,
            _render_chat(working_history),
        )

    except Exception as exc:
        working_history[-1] = {
            "role": "assistant",
            "content": f"Coach Chat error: {exc}",
            "thinking": False,
        }

        yield (
            "",
            working_history,
            _render_chat(working_history),
        )


def build_chat_page(
    workspace_name,
    credit_balance=None,
    visible=False,
):
    """
    Full-page Coach Chat with custom rendering and live streaming.
    """

    css = """
    /* =========================
       PAGE
       ========================= */

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
        margin: 0 auto 30px !important;
        padding: 10px 14px !important;
        border-radius: 16px !important;

        background:
            linear-gradient(
                180deg,
                rgba(17, 22, 40, .98),
                rgba(10, 14, 29, .98)
            ) !important;

        border:
            1px solid rgba(168, 85, 247, .58) !important;

        box-shadow:
            0 0 18px rgba(139, 92, 246, .10) !important;

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
            0 0 10px rgba(34, 211, 238, .60);
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

    #coach-chat-window {
        width: min(900px, 96%) !important;
        height: 320px !important;
        margin: 0 auto 30px !important;
        padding: 22px 24px !important;

        background:
            radial-gradient(
                circle at 18% 0%,
                rgba(139, 92, 246, .16),
                transparent 38%
            ),
            linear-gradient(
                180deg,
                #12172a 0%,
                #0d1222 100%
            ) !important;

        border:
            1px solid rgba(168, 85, 247, .72) !important;

        border-radius: 20px !important;

        box-shadow:
            inset 0 0 32px rgba(139, 92, 246, .06),
            0 14px 30px rgba(0, 0, 0, .30) !important;

        overflow-y: auto !important;
        box-sizing: border-box !important;
    }

    #coach-chat-window,
    #coach-chat-window > div {
        background-color: transparent !important;
    }

    #coach-chat-window > div {
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
    }


    /* =========================
       MESSAGE ROWS
       ========================= */

    .cc-message-row {
        width: 100%;
        box-sizing: border-box;
        margin-bottom: 26px;
    }

    .cc-message-row:last-child {
        margin-bottom: 0;
    }


    /* =========================
       COACH
       ========================= */

    .cc-assistant-row {
        display: block;
    }

    .cc-coach-label {
        margin-bottom: 10px;
        color: rgba(34, 211, 238, .82);
        font-size: 11px;
        font-weight: 800;
        letter-spacing: .08em;
        text-transform: uppercase;
    }

    .cc-assistant-message {
        width: 100%;
        color: #eef2ff;
        font-size: 16px;
        line-height: 1.72;

        background:
            rgba(255, 255, 255, .015);

        border-left:
            2px solid rgba(34, 211, 238, .40);

        padding: 3px 0 3px 18px;
        margin: 0;
        box-sizing: border-box;
    }

    .cc-assistant-message .cc-line {
        margin-bottom: 12px;
    }

    .cc-assistant-message .cc-bullet {
        margin: 7px 0 7px 14px;
    }


    /* =========================
       THINKING INDICATOR
       ========================= */

    .cc-thinking {
        display: flex;
        align-items: center;
        gap: 6px;

        color: rgba(226, 232, 240, .70);

        border-left:
            2px solid rgba(34, 211, 238, .40);

        padding: 8px 0 8px 18px;
        min-height: 28px;
    }

    .cc-thinking-dot {
        width: 6px;
        height: 6px;
        border-radius: 999px;
        background: #22d3ee;
        opacity: .35;
        animation: cc-thinking-pulse 1.15s infinite ease-in-out;
    }

    .cc-thinking-dot:nth-child(2) {
        animation-delay: .15s;
    }

    .cc-thinking-dot:nth-child(3) {
        animation-delay: .30s;
    }

    .cc-thinking-text {
        margin-left: 6px;
        font-size: 14px;
        letter-spacing: .01em;
    }

    @keyframes cc-thinking-pulse {
        0%, 80%, 100% {
            opacity: .25;
            transform: translateY(0);
        }

        40% {
            opacity: 1;
            transform: translateY(-3px);
        }
    }


    /* =========================
       USER MESSAGE
       ========================= */

    .cc-user-row {
        display: flex;
        justify-content: flex-end;
    }

    .cc-user-message {
        width: auto;
        max-width: 72%;
        padding: 11px 16px;
        color: white;
        font-size: 15px;
        line-height: 1.55;

        background:
            linear-gradient(
                135deg,
                rgba(124, 58, 237, .95),
                rgba(190, 24, 93, .82)
            );

        border:
            1px solid rgba(244, 114, 182, .50);

        border-radius: 16px;

        box-shadow:
            0 7px 18px rgba(0, 0, 0, .22);
    }

    .cc-user-message .cc-line {
        margin-bottom: 5px;
    }


    /* =========================
       SPACING / EMPTY
       ========================= */

    .cc-space {
        height: 10px;
    }

    .cc-line:last-child {
        margin-bottom: 0;
    }

    .cc-empty {
        width: 100%;
        padding-top: 12px;
        color: rgba(226, 232, 240, .46);
        font-size: 15px;
        text-align: center;
    }


    /* =========================
       SCROLLBAR
       ========================= */

    #coach-chat-window::-webkit-scrollbar {
        width: 8px;
    }

    #coach-chat-window::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, .02);
    }

    #coach-chat-window::-webkit-scrollbar-thumb {
        background:
            linear-gradient(
                180deg,
                #7c3aed,
                #9333ea
            );

        border-radius: 10px;
    }


    /* =========================
       COMPOSER
       ========================= */

    #coach-chat-composer {
        width: min(900px, 96%) !important;
        margin: 0 auto !important;
        padding: 8px 9px 8px 13px !important;

        border-radius: 18px !important;

        background:
            linear-gradient(
                180deg,
                rgba(18, 23, 42, .99),
                rgba(10, 13, 26, .99)
            ) !important;

        border:
            1px solid rgba(168, 85, 247, .72) !important;

        box-shadow:
            0 10px 28px rgba(0, 0, 0, .35),
            0 0 18px rgba(139, 92, 246, .10) !important;

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
        color: rgba(226, 232, 240, .45) !important;
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
            0 0 17px rgba(236, 72, 153, .34) !important;
    }

    #coach-chat-send:hover {
        transform: translateY(-1px) !important;
    }


    /* =========================
       MOBILE
       ========================= */

    @media (max-width: 700px) {
        #coach-chat-header,
        #coach-chat-window,
        #coach-chat-composer {
            width: 100% !important;
        }

        #coach-chat-window {
            height: 54vh !important;
            padding: 17px !important;
        }

        .cc-user-message {
            max-width: 88%;
        }

        .cc-assistant-message,
        .cc-thinking {
            padding-left: 14px;
        }
    }
    """

    with gr.Column(
        visible=visible,
        elem_id="chat-page",
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

        history_state = gr.State([])

        chat_display = gr.HTML(
            value=_render_chat([]),
            elem_id="coach-chat-window",
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
                history_state,
                workspace_name,
            ],
            outputs=[
                message_box,
                history_state,
                chat_display,
            ],
            show_progress="hidden",
        )

        message_box.submit(
            fn=_respond,
            inputs=[
                message_box,
                history_state,
                workspace_name,
            ],
            outputs=[
                message_box,
                history_state,
                chat_display,
            ],
            show_progress="hidden",
        )

    return chat_page


    
