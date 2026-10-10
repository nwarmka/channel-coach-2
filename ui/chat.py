import html
import time

import gradio as gr

from features import stream_creator_coach
from database import (
    create_coach_chat,
    delete_coach_chat,
    get_coach_chat,
    get_coach_chats,
    rename_coach_chat,
    save_coach_chat,
    set_coach_chat_pinned,
)


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

                        <div class="cc-thinking-card" role="status" aria-live="polite">
                            <div class="cc-thinking-main">
                                <span class="cc-chat-spinner" aria-hidden="true"></span>
                                <span class="cc-thinking-text">
                                    Channel Coach is working on your answer
                                </span>
                                <span class="cc-thinking-dots" aria-hidden="true">
                                    <span class="cc-thinking-dot"></span>
                                    <span class="cc-thinking-dot"></span>
                                    <span class="cc-thinking-dot"></span>
                                </span>
                            </div>

                            <div class="cc-thinking-progress" aria-hidden="true">
                                <span></span>
                            </div>

                            <div class="cc-chat-tip">
                                <strong>TIP:</strong>
                                Ask Coach Chat to turn one idea into a title, hook, and posting plan.
                            </div>
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


def _auto_chat_title(message):
    words = str(message or "").strip().replace("\n", " ").split()
    title = " ".join(words[:7]).strip()
    if len(title) > 56:
        title = title[:53].rstrip() + "..."
    return title or "New Chat"


def _chat_choices(user_id):
    chats = get_coach_chats(user_id)
    choices = []
    for chat in chats:
        prefix = "📌 " if chat.get("is_pinned") else "🕘 "
        choices.append((prefix + (chat.get("title") or "New Chat"), chat.get("id")))
    return choices


def _refresh_chat_picker(workspace_name, selected=None):
    user_id = (workspace_name or "main").strip() or "main"
    choices = _chat_choices(user_id)
    values = [value for _, value in choices]
    value = selected if selected in values else (values[0] if values else None)
    return gr.update(choices=choices, value=value)


def _new_chat(workspace_name):
    return [], None, _render_chat([]), "", _refresh_chat_picker(workspace_name, None), ""


def _load_chat(chat_id, workspace_name):
    if not chat_id:
        return [], None, _render_chat([]), ""
    user_id = (workspace_name or "main").strip() or "main"
    chat = get_coach_chat(chat_id, user_id)
    if not chat:
        return [], None, _render_chat([]), ""
    history = list(chat.get("messages") or [])
    return history, chat_id, _render_chat(history), chat.get("title") or "New Chat"


def _rename_selected(chat_id, title, workspace_name):
    user_id = (workspace_name or "main").strip() or "main"
    if chat_id and str(title or "").strip():
        rename_coach_chat(chat_id, title, user_id)
    return _refresh_chat_picker(user_id, chat_id)


def _toggle_pin(chat_id, workspace_name):
    user_id = (workspace_name or "main").strip() or "main"
    if chat_id:
        chat = get_coach_chat(chat_id, user_id)
        if chat:
            set_coach_chat_pinned(chat_id, not bool(chat.get("is_pinned")), user_id)
    return _refresh_chat_picker(user_id, chat_id)


def _delete_selected(chat_id, workspace_name):
    user_id = (workspace_name or "main").strip() or "main"
    if chat_id:
        delete_coach_chat(chat_id, user_id)
    return [], None, _render_chat([]), "", _refresh_chat_picker(user_id, None)


def _respond(message, history, chat_id, workspace_name):
    message = (message or "").strip()
    history = list(history or [])
    user_id = (workspace_name or "main").strip() or "main"

    if not message:
        yield "", history, chat_id, _render_chat(history), _refresh_chat_picker(user_id, chat_id), gr.update()
        return

    prior_history = [dict(item) for item in history if not item.get("thinking")]
    working_history = prior_history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": "", "thinking": True},
    ]

    yield "", working_history, chat_id, _render_chat(working_history), gr.update(), gr.update()

    partial_reply = ""
    last_ui_update = 0.0
    try:
        for delta in stream_creator_coach(
            message, user_id=user_id, conversation_history=prior_history
        ):
            partial_reply += delta
            working_history[-1] = {
                "role": "assistant", "content": partial_reply, "thinking": False
            }
            now = time.monotonic()
            if now - last_ui_update >= 0.05:
                yield "", working_history, chat_id, _render_chat(working_history), gr.update(), gr.update()
                last_ui_update = now

        working_history[-1] = {
            "role": "assistant",
            "content": partial_reply or "I couldn't generate a response.",
            "thinking": False,
        }
        final_history = [dict(item) for item in working_history if not item.get("thinking")]

        current_chat_id = chat_id
        title = None
        if current_chat_id:
            save_coach_chat(current_chat_id, final_history, user_id)
            chat = get_coach_chat(current_chat_id, user_id)
            title = (chat or {}).get("title") or "New Chat"
        else:
            title = _auto_chat_title(message)
            current_chat_id = create_coach_chat(title, final_history, user_id)

        yield (
            "", final_history, current_chat_id, _render_chat(final_history),
            _refresh_chat_picker(user_id, current_chat_id), gr.update(value=title or "")
        )
    except Exception as exc:
        working_history[-1] = {
            "role": "assistant", "content": f"Coach Chat error: {exc}", "thinking": False
        }
        yield "", working_history, chat_id, _render_chat(working_history), gr.update(), gr.update()


def build_chat_page(
    workspace_name,
    credit_balance=None,
    visible=False,
):
    """Full-page Coach Chat with a ChatGPT-style conversation sidebar."""

    css = """
    #chat-page { min-height:78vh!important; background:transparent!important; border:none!important; box-shadow:none!important; }
    #coach-chat-shell { width:min(1180px,98%)!important; margin:0 auto!important; gap:18px!important; align-items:stretch!important; }
    /* Gradio rows may wrap their columns; force the desktop chat to stay in two columns. */
    @media (min-width:801px) {
      #coach-chat-shell { display:flex!important; flex-flow:row nowrap!important; align-items:flex-start!important; }
      #coach-chat-shell > .gradio-column,
      #coach-chat-shell > div { min-width:0!important; }
      #coach-chat-sidebar { flex:0 0 260px!important; width:260px!important; min-width:260px!important; max-width:260px!important; }
      #coach-chat-main { flex:1 1 0%!important; width:auto!important; min-width:0!important; max-width:none!important; }
    }

    #coach-chat-sidebar { flex:0 0 260px!important; max-width:260px!important; min-width:230px!important; height:650px!important; padding:12px 10px!important; background:#080b12!important; border-right:1px solid rgba(148,163,184,.16)!important; border-radius:18px!important; overflow:hidden!important; }
    #coach-chat-main { min-width:0!important; flex:1 1 auto!important; }
    
    #coach-new-chat { width:100%!important; justify-content:flex-start!important; text-align:left!important; background:transparent!important; border:none!important; box-shadow:none!important; color:#f8fafc!important; font-weight:700!important; }
    #coach-new-chat:hover { background:rgba(148,163,184,.09)!important; }
    /* Native Gradio dropdown avoids the radio group's broken multi-column grid. */
    #coach-chat-picker { width:100%!important; min-width:0!important; max-width:100%!important; }
    #coach-chat-picker input { min-width:0!important; text-overflow:ellipsis!important; }
    #coach-chat-picker::before { content:"PINNED / RECENT"; display:block; color:rgba(226,232,240,.46); font-size:.68rem; font-weight:800; letter-spacing:.08em; padding:12px 9px 5px; }
    #coach-chat-sidebar { overflow-x:hidden!important; }
    #coach-chat-window { overflow-x:hidden!important; overscroll-behavior:contain!important; }
    #coach-chat-actions { margin-top:auto!important; padding-top:10px!important; border-top:1px solid rgba(148,163,184,.12)!important; }
    #coach-chat-actions textarea { min-height:38px!important; font-size:.82rem!important; }
    #coach-chat-actions button { min-width:0!important; font-size:.76rem!important; padding:6px 7px!important; }
    #coach-chat-header { margin:0 0 10px!important; padding:6px 8px!important; border-radius:0!important; background:transparent!important; border:none!important; }
    .cc-chat-header-inner { display:flex; align-items:center; gap:9px; }
    .cc-chat-orb { color:#22d3ee; } .cc-chat-title { color:#f7f7ff; font-weight:800; }
    #coach-chat-window { height:530px!important; overflow-y:auto!important; margin:0 0 14px!important; padding:24px 26px!important; background:#0d1222!important; border:1px solid rgba(168,85,247,.55)!important; border-radius:20px!important; }
    .cc-message-row { margin-bottom:18px; } .cc-user-row { display:flex; justify-content:flex-end; }
    .cc-user-message { max-width:78%; padding:11px 14px; border-radius:16px 16px 4px 16px; background:linear-gradient(135deg,#7c3aed,#a855f7); color:white; }
    .cc-coach-label { color:#22d3ee; font-size:.72rem; font-weight:800; margin-bottom:6px; }
    .cc-assistant-message,.cc-thinking { color:#eef2ff; line-height:1.55; padding-left:10px; }
    .cc-bullet { margin:4px 0; } .cc-space { height:8px; }
    .cc-empty { color:rgba(226,232,240,.55); text-align:center; padding-top:180px; }
    .cc-thinking-card {
        max-width:560px;
        padding:12px 14px;
        border:1px solid rgba(34,211,238,.20);
        border-radius:14px;
        background:linear-gradient(180deg,rgba(15,23,42,.72),rgba(13,18,34,.92));
        box-shadow:0 0 22px rgba(34,211,238,.05);
    }
    .cc-thinking-main { display:flex; align-items:center; gap:9px; color:#eef2ff; min-height:22px; }
    .cc-chat-spinner {
        width:15px; height:15px; flex:0 0 15px;
        border:2px solid rgba(34,211,238,.22);
        border-top-color:#22d3ee;
        border-right-color:#a855f7;
        border-radius:50%;
        animation:ccChatSpin .8s linear infinite;
    }
    .cc-thinking-text { font-size:.9rem; font-weight:600; color:#e2e8f0; }
    .cc-thinking-dots { display:inline-flex; align-items:center; gap:4px; margin-left:1px; }
    .cc-thinking-dot {
        display:inline-block; width:5px; height:5px; border-radius:50%;
        background:#22d3ee; opacity:.35;
        animation:ccChatDot 1.1s ease-in-out infinite;
    }
    .cc-thinking-dot:nth-child(2) { animation-delay:.16s; }
    .cc-thinking-dot:nth-child(3) { animation-delay:.32s; }
    .cc-thinking-progress {
        position:relative; height:3px; margin-top:10px; overflow:hidden;
        border-radius:999px; background:rgba(148,163,184,.12);
    }
    .cc-thinking-progress span {
        position:absolute; top:0; left:0; width:38%; height:100%;
        border-radius:inherit;
        background:linear-gradient(90deg,#22d3ee,#8b5cf6,#ec4899);
        animation:ccChatProgress 1.15s ease-in-out infinite;
    }
    .cc-chat-tip {
        margin-top:10px; padding-top:9px;
        border-top:1px solid rgba(148,163,184,.10);
        color:rgba(226,232,240,.68); font-size:.78rem; line-height:1.45;
    }
    .cc-chat-tip strong { color:#ec4899; font-size:.7rem; letter-spacing:.08em; }
    @keyframes ccChatSpin { to { transform:rotate(360deg); } }
    @keyframes ccChatDot {
        0%,70%,100% { opacity:.28; transform:translateY(0); }
        35% { opacity:1; transform:translateY(-2px); }
    }
    @keyframes ccChatProgress {
        0% { transform:translateX(-115%); }
        100% { transform:translateX(300%); }
    }
    @media (prefers-reduced-motion:reduce) {
        .cc-chat-spinner,.cc-thinking-dot,.cc-thinking-progress span { animation:none!important; }
    }
    #coach-chat-composer { padding:10px 12px!important; border:1px solid rgba(168,85,247,.72)!important; border-radius:18px!important; background:#0d1222!important; }
    #coach-chat-input, #coach-chat-input > div { background:transparent!important; border:none!important; box-shadow:none!important; }
    #coach-chat-input textarea { background:transparent!important; border:none!important; color:white!important; }
    #coach-chat-send { min-width:42px!important; width:42px!important; height:42px!important; border-radius:13px!important; background:linear-gradient(135deg,#7c3aed,#ec4899)!important; border:none!important; }
    @media (max-width:800px) {
        #coach-chat-shell { flex-direction:column!important; width:100%!important; }
        #coach-chat-sidebar { flex:none!important; max-width:none!important; min-width:0!important; width:100%!important; height:auto!important; max-height:260px!important; border-right:none!important; border-bottom:1px solid rgba(148,163,184,.16)!important; }
        #coach-chat-picker { max-height:120px!important; }
        #coach-chat-window { height:52vh!important; padding:17px!important; }
        .cc-user-message { max-width:88%; }
    }
    """

    with gr.Column(visible=visible, elem_id="chat-page") as chat_page:
        gr.HTML(f"<style>{css}</style>")

        history_state = gr.State([])
        chat_id_state = gr.State(None)

        with gr.Row(elem_id="coach-chat-shell"):
            with gr.Column(elem_id="coach-chat-sidebar"):
                new_chat_button = gr.Button("＋  New chat", elem_id="coach-new-chat")
                chat_picker = gr.Dropdown(
                    choices=[],
                    label="Saved chats",
                    show_label=False,
                    interactive=True,
                    elem_id="coach-chat-picker",
                )

                with gr.Column(elem_id="coach-chat-actions"):
                    rename_box = gr.Textbox(
                        value="",
                        visible=False,
                        show_label=False,
                    )
                    with gr.Accordion("Chat options", open=False, elem_id="coach-chat-options"):
                        with gr.Row():
                            rename_button = gr.Button("Rename")
                            pin_button = gr.Button("Pin / Unpin")
                            delete_button = gr.Button("Delete", variant="stop")

            with gr.Column(elem_id="coach-chat-main"):
                with gr.Row(elem_id="coach-chat-header"):
                    gr.HTML('<div class="cc-chat-header-inner"><span class="cc-chat-orb">✦</span><span class="cc-chat-title">COACH CHAT</span></div>')

                chat_display = gr.HTML(value=_render_chat([]), elem_id="coach-chat-window")

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

        new_chat_button.click(
            fn=_new_chat,
            inputs=[workspace_name],
            outputs=[history_state, chat_id_state, chat_display, rename_box, chat_picker, message_box],
            show_progress="hidden",
        )
        # Choices start empty at build time; reload them when the user opens
        # the selector, including after a Render restart or fresh login.
        chat_picker.focus(
            fn=_refresh_chat_picker,
            inputs=[workspace_name],
            outputs=[chat_picker],
            show_progress="hidden",
        )
        chat_picker.change(
            fn=_load_chat,
            inputs=[chat_picker, workspace_name],
            outputs=[history_state, chat_id_state, chat_display, rename_box],
            show_progress="hidden",
        )
        rename_button.click(
            fn=_rename_selected,
            inputs=[chat_id_state, rename_box, workspace_name],
            outputs=[chat_picker],
            show_progress="hidden",
        )
        pin_button.click(
            fn=_toggle_pin,
            inputs=[chat_id_state, workspace_name],
            outputs=[chat_picker],
            show_progress="hidden",
        )
        delete_button.click(
            fn=_delete_selected,
            inputs=[chat_id_state, workspace_name],
            outputs=[history_state, chat_id_state, chat_display, rename_box, chat_picker],
            show_progress="hidden",
        )

        send_inputs = [message_box, history_state, chat_id_state, workspace_name]
        send_outputs = [message_box, history_state, chat_id_state, chat_display, chat_picker, rename_box]
        send_button.click(fn=_respond, inputs=send_inputs, outputs=send_outputs, show_progress="hidden")
        message_box.submit(fn=_respond, inputs=send_inputs, outputs=send_outputs, show_progress="hidden")

    return chat_page


    
