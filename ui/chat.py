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


def _auto_chat_title(message):
    words = str(message or "").strip().replace("\n", " ").split()
    title = " ".join(words[:7]).strip()
    if len(title) > 56:
        title = title[:53].rstrip() + "..."
    return title or "New Chat"



MAX_CHAT_ROWS = 18


def _get_chat_rows(user_id):
    chats = get_coach_chats(user_id) or []
    rows = []
    for chat in chats[:MAX_CHAT_ROWS]:
        rows.append(
            {
                "id": chat.get("id"),
                "title": chat.get("title") or "New Chat",
                "is_pinned": bool(chat.get("is_pinned")),
            }
        )
    return rows


def _sidebar_updates(user_id, selected=None):
    rows = _get_chat_rows(user_id)
    ids = [row["id"] for row in rows]
    updates = []

    for index in range(MAX_CHAT_ROWS):
        if index < len(rows):
            row = rows[index]
            prefix = "📌  " if row["is_pinned"] else ""
            updates.append(
                gr.update(
                    value=prefix + row["title"],
                    visible=True,
                    variant="secondary" if row["id"] == selected else "secondary",
                )
            )
        else:
            updates.append(gr.update(value="", visible=False))

    return ids, updates


def _new_chat(workspace_name):
    user_id = (workspace_name or "main").strip() or "main"
    ids, updates = _sidebar_updates(user_id, None)
    return [[], None, _render_chat([]), "", ids, "", *updates]


def _load_chat_slot(slot_index, chat_ids, workspace_name):
    chat_ids = list(chat_ids or [])
    if slot_index >= len(chat_ids):
        return [], None, _render_chat([]), ""

    chat_id = chat_ids[slot_index]
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
    ids, updates = _sidebar_updates(user_id, chat_id)
    return [ids, *updates]


def _toggle_pin(chat_id, workspace_name):
    user_id = (workspace_name or "main").strip() or "main"
    if chat_id:
        chat = get_coach_chat(chat_id, user_id)
        if chat:
            set_coach_chat_pinned(
                chat_id,
                not bool(chat.get("is_pinned")),
                user_id,
            )
    ids, updates = _sidebar_updates(user_id, chat_id)
    return [ids, *updates]


def _delete_selected(chat_id, workspace_name):
    user_id = (workspace_name or "main").strip() or "main"
    if chat_id:
        delete_coach_chat(chat_id, user_id)
    ids, updates = _sidebar_updates(user_id, None)
    return [[], None, _render_chat([]), "", ids, *updates]


def _respond(message, history, chat_id, workspace_name):
    message = (message or "").strip()
    history = list(history or [])
    user_id = (workspace_name or "main").strip() or "main"

    if not message:
        ids, updates = _sidebar_updates(user_id, chat_id)
        yield ["", history, chat_id, _render_chat(history), ids, gr.update(), *updates]
        return

    prior_history = [
        dict(item) for item in history if not item.get("thinking")
    ]
    working_history = prior_history + [
        {"role": "user", "content": message},
        {
            "role": "assistant",
            "content": "",
            "thinking": True,
        },
    ]

    neutral_rows = [gr.update() for _ in range(MAX_CHAT_ROWS)]
    yield [
        "",
        working_history,
        chat_id,
        _render_chat(working_history),
        gr.update(),
        gr.update(),
        *neutral_rows,
    ]

    partial_reply = ""
    last_ui_update = 0.0

    try:
        for delta in stream_creator_coach(
            message,
            user_id=user_id,
            conversation_history=prior_history,
        ):
            partial_reply += delta
            working_history[-1] = {
                "role": "assistant",
                "content": partial_reply,
                "thinking": False,
            }

            now = time.monotonic()
            if now - last_ui_update >= 0.05:
                yield [
                    "",
                    working_history,
                    chat_id,
                    _render_chat(working_history),
                    gr.update(),
                    gr.update(),
                    *neutral_rows,
                ]
                last_ui_update = now

        working_history[-1] = {
            "role": "assistant",
            "content": partial_reply or "I couldn't generate a response.",
            "thinking": False,
        }
        final_history = [
            dict(item)
            for item in working_history
            if not item.get("thinking")
        ]

        current_chat_id = chat_id
        if current_chat_id:
            save_coach_chat(
                current_chat_id,
                final_history,
                user_id,
            )
            chat = get_coach_chat(current_chat_id, user_id)
            title = (chat or {}).get("title") or "New Chat"
        else:
            title = _auto_chat_title(message)
            current_chat_id = create_coach_chat(
                title,
                final_history,
                user_id,
            )

        ids, updates = _sidebar_updates(
            user_id,
            current_chat_id,
        )
        yield [
            "",
            final_history,
            current_chat_id,
            _render_chat(final_history),
            ids,
            gr.update(value=title or ""),
            *updates,
        ]

    except Exception as exc:
        working_history[-1] = {
            "role": "assistant",
            "content": f"Coach Chat error: {exc}",
            "thinking": False,
        }
        yield [
            "",
            working_history,
            chat_id,
            _render_chat(working_history),
            gr.update(),
            gr.update(),
            *neutral_rows,
        ]



def _make_chat_slot_loader(slot_index):
    def load_slot(chat_ids, workspace_name):
        return _load_chat_slot(
            slot_index,
            chat_ids,
            workspace_name,
        )
    return load_slot

def build_chat_page(
    workspace_name,
    credit_balance=None,
    visible=False,
):
    """Coach Chat with a flat, ChatGPT-style conversation sidebar."""

    css = """
    #chat-page {
        min-height:78vh!important;
        background:transparent!important;
        border:none!important;
        box-shadow:none!important;
    }

    #coach-chat-shell {
        width:min(1220px,98%)!important;
        margin:0 auto!important;
        gap:0!important;
        align-items:stretch!important;
    }

    #coach-chat-sidebar {
        flex:0 0 270px!important;
        max-width:270px!important;
        min-width:240px!important;
        height:650px!important;
        padding:12px 8px!important;
        background:#05070b!important;
        border:none!important;
        border-right:1px solid rgba(148,163,184,.14)!important;
        border-radius:0!important;
        overflow:hidden!important;
    }

    #coach-new-chat {
        width:100%!important;
        justify-content:flex-start!important;
        text-align:left!important;
        padding:11px 12px!important;
        margin-bottom:12px!important;
        background:transparent!important;
        border:none!important;
        box-shadow:none!important;
        color:#f1f5f9!important;
        font-size:.98rem!important;
        font-weight:600!important;
        border-radius:9px!important;
    }

    #coach-new-chat:hover {
        background:rgba(148,163,184,.10)!important;
    }

    .cc-section-label {
        padding:14px 12px 6px;
        color:rgba(226,232,240,.62);
        font-size:.72rem;
        font-weight:700;
    }

    #coach-chat-list {
        height:465px!important;
        max-height:465px!important;
        overflow-y:auto!important;
        overflow-x:hidden!important;
        gap:1px!important;
        padding:0!important;
        background:transparent!important;
        border:none!important;
        box-shadow:none!important;
    }

    #coach-chat-list::-webkit-scrollbar {
        width:6px;
    }

    #coach-chat-list::-webkit-scrollbar-thumb {
        background:rgba(148,163,184,.25);
        border-radius:999px;
    }

    .cc-chat-row {
        width:100%!important;
        min-height:38px!important;
        height:auto!important;
        justify-content:flex-start!important;
        text-align:left!important;
        padding:8px 12px!important;
        margin:0!important;
        background:transparent!important;
        border:none!important;
        box-shadow:none!important;
        color:#cbd5e1!important;
        font-size:.9rem!important;
        font-weight:400!important;
        border-radius:8px!important;
        white-space:nowrap!important;
        overflow:hidden!important;
        text-overflow:ellipsis!important;
    }

    .cc-chat-row:hover {
        background:rgba(148,163,184,.10)!important;
        color:#fff!important;
    }

    #coach-chat-tools {
        margin-top:auto!important;
        padding:8px 6px 0!important;
        border-top:1px solid rgba(148,163,184,.10)!important;
        gap:5px!important;
    }

    #coach-chat-tools button {
        min-width:0!important;
        border:none!important;
        background:transparent!important;
        box-shadow:none!important;
        color:rgba(226,232,240,.62)!important;
        font-size:.72rem!important;
        padding:5px 6px!important;
    }

    #coach-chat-tools button:hover {
        color:white!important;
        background:rgba(148,163,184,.08)!important;
    }

    #coach-chat-main {
        min-width:0!important;
        flex:1 1 auto!important;
        height:650px!important;
        padding:0 0 0 22px!important;
        background:transparent!important;
        overflow:hidden!important;
    }

    #coach-chat-header {
        height:42px!important;
        min-height:42px!important;
        margin:0!important;
        padding:8px 4px!important;
        background:transparent!important;
        border:none!important;
        box-shadow:none!important;
    }

    .cc-chat-header-inner {
        display:flex;
        align-items:center;
        gap:8px;
    }

    .cc-chat-orb {
        color:#22d3ee;
    }

    .cc-chat-title {
        color:#f7f7ff;
        font-weight:700;
        font-size:.86rem;
    }

    #coach-chat-window {
        height:530px!important;
        min-height:0!important;
        max-height:530px!important;
        overflow-y:auto!important;
        overflow-x:hidden!important;
        margin:0!important;
        padding:20px 18px!important;
        background:#0d1222!important;
        border:none!important;
        border-radius:14px!important;
        box-shadow:none!important;
    }

    .cc-message-row {
        margin-bottom:18px;
    }

    .cc-user-row {
        display:flex;
        justify-content:flex-end;
    }

    .cc-user-message {
        max-width:78%;
        padding:11px 14px;
        border-radius:16px 16px 4px 16px;
        background:linear-gradient(135deg,#7c3aed,#a855f7);
        color:white;
    }

    .cc-coach-label {
        color:#22d3ee;
        font-size:.72rem;
        font-weight:800;
        margin-bottom:6px;
    }

    .cc-assistant-message,
    .cc-thinking {
        color:#eef2ff;
        line-height:1.55;
        padding-left:10px;
    }

    .cc-bullet {
        margin:4px 0;
    }

    .cc-space {
        height:8px;
    }

    .cc-empty {
        color:rgba(226,232,240,.55);
        text-align:center;
        padding-top:190px;
    }

    .cc-thinking-dot {
        display:inline-block;
        width:6px;
        height:6px;
        border-radius:50%;
        background:#22d3ee;
        margin-right:4px;
    }

    #coach-chat-composer {
        height:64px!important;
        margin-top:12px!important;
        padding:10px 12px!important;
        border:1px solid rgba(168,85,247,.52)!important;
        border-radius:18px!important;
        background:#0d1222!important;
    }

    #coach-chat-input,
    #coach-chat-input > div {
        background:transparent!important;
        border:none!important;
        box-shadow:none!important;
    }

    #coach-chat-input textarea {
        background:transparent!important;
        border:none!important;
        color:white!important;
    }

    #coach-chat-send {
        min-width:42px!important;
        width:42px!important;
        height:42px!important;
        border-radius:13px!important;
        background:linear-gradient(135deg,#7c3aed,#ec4899)!important;
        border:none!important;
    }

    @media (max-width:800px) {
        #coach-chat-shell {
            flex-direction:column!important;
            width:100%!important;
        }

        #coach-chat-sidebar {
            flex:none!important;
            max-width:none!important;
            min-width:0!important;
            width:100%!important;
            height:auto!important;
            max-height:250px!important;
            border-right:none!important;
            border-bottom:1px solid rgba(148,163,184,.14)!important;
        }

        #coach-chat-list {
            height:115px!important;
            max-height:115px!important;
        }

        #coach-chat-main {
            height:auto!important;
            padding:12px 0 0!important;
        }

        #coach-chat-window {
            height:52vh!important;
            max-height:52vh!important;
            padding:16px!important;
        }

        .cc-user-message {
            max-width:88%;
        }
    }
    """

    with gr.Column(
        visible=visible,
        elem_id="chat-page",
    ) as chat_page:
        gr.HTML(f"<style>{css}</style>")

        history_state = gr.State([])
        chat_id_state = gr.State(None)
        chat_ids_state = gr.State([])

        with gr.Row(elem_id="coach-chat-shell"):
            with gr.Column(elem_id="coach-chat-sidebar"):
                new_chat_button = gr.Button(
                    "✎  New chat",
                    elem_id="coach-new-chat",
                )

                gr.HTML(
                    '<div class="cc-section-label">Recents</div>'
                )

                chat_buttons = []
                with gr.Column(elem_id="coach-chat-list"):
                    for index in range(MAX_CHAT_ROWS):
                        button = gr.Button(
                            "",
                            visible=False,
                            elem_classes=["cc-chat-row"],
                        )
                        chat_buttons.append(button)

                rename_box = gr.Textbox(
                    value="",
                    visible=False,
                    show_label=False,
                )

                with gr.Row(elem_id="coach-chat-tools"):
                    rename_button = gr.Button("Rename")
                    pin_button = gr.Button("Pin")
                    delete_button = gr.Button("Delete")

            with gr.Column(elem_id="coach-chat-main"):
                with gr.Row(elem_id="coach-chat-header"):
                    gr.HTML(
                        '<div class="cc-chat-header-inner">'
                        '<span class="cc-chat-orb">✦</span>'
                        '<span class="cc-chat-title">COACH CHAT</span>'
                        '</div>'
                    )

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

        sidebar_outputs = [chat_ids_state, *chat_buttons]

        new_chat_button.click(
            fn=_new_chat,
            inputs=[workspace_name],
            outputs=[
                history_state,
                chat_id_state,
                chat_display,
                rename_box,
                chat_ids_state,
                message_box,
                *chat_buttons,
            ],
            show_progress="hidden",
        )

        for index, button in enumerate(chat_buttons):
            button.click(
                fn=_make_chat_slot_loader(index),
                inputs=[chat_ids_state, workspace_name],
                outputs=[
                    history_state,
                    chat_id_state,
                    chat_display,
                    rename_box,
                ],
                show_progress="hidden",
            )

        rename_button.click(
            fn=_rename_selected,
            inputs=[
                chat_id_state,
                rename_box,
                workspace_name,
            ],
            outputs=sidebar_outputs,
            show_progress="hidden",
        )

        pin_button.click(
            fn=_toggle_pin,
            inputs=[
                chat_id_state,
                workspace_name,
            ],
            outputs=sidebar_outputs,
            show_progress="hidden",
        )

        delete_button.click(
            fn=_delete_selected,
            inputs=[
                chat_id_state,
                workspace_name,
            ],
            outputs=[
                history_state,
                chat_id_state,
                chat_display,
                rename_box,
                chat_ids_state,
                *chat_buttons,
            ],
            show_progress="hidden",
        )

        send_inputs = [
            message_box,
            history_state,
            chat_id_state,
            workspace_name,
        ]
        send_outputs = [
            message_box,
            history_state,
            chat_id_state,
            chat_display,
            chat_ids_state,
            rename_box,
            *chat_buttons,
        ]

        send_button.click(
            fn=_respond,
            inputs=send_inputs,
            outputs=send_outputs,
            show_progress="hidden",
        )
        message_box.submit(
            fn=_respond,
            inputs=send_inputs,
            outputs=send_outputs,
            show_progress="hidden",
        )

    return chat_page


    
