"""Channel Coach: private Content Ideas Inbox."""
import html
from urllib.parse import urlsplit
import gradio as gr
from auth import create_supabase_client, empty_saved_session

TABLE = "content_ideas_inbox"

def _authenticated_client(saved_session):
    if not isinstance(saved_session, dict):
        raise ValueError("Please sign in to save and view your ideas.")
    access = str(saved_session.get("access_token") or "")
    refresh = str(saved_session.get("refresh_token") or "")
    if not access or not refresh:
        raise ValueError("Please sign in to save and view your ideas.")
    client = create_supabase_client()
    response = client.auth.set_session(access, refresh)
    if not response.user or not response.session:
        raise ValueError("Your login has expired. Please sign in again.")
    verified = client.auth.get_user()
    user = getattr(verified, "user", None)
    if not user or str(user.id) != str(response.user.id):
        raise ValueError("Please sign in again.")
    updated_session = {
        "access_token": response.session.access_token,
        "refresh_token": response.session.refresh_token,
        "user_id": str(user.id),
        "email": user.email or saved_session.get("email", ""),
    }
    return client, str(user.id), updated_session

def _safe_link(url):
    url = (url or "").strip()
    if not url:
        return ""
    parsed = urlsplit(url)
    if parsed.scheme.lower() not in ("https", "http") or not parsed.netloc:
        return ""
    safe_url = html.escape(url, quote=True)
    return ('<p style="margin:8px 0"><a href="' + safe_url
            + '" target="_blank" rel="noopener noreferrer">'
            + html.escape(url[:140]) + "</a></p>")

def _render_ideas(rows):
    if not rows:
        return ('<div style="padding:16px;border:1px solid #64748b55;'
                'border-radius:12px">No saved ideas yet. Add your first one above! 💡</div>')
    cards = []
    for row in rows:
        title = html.escape(str(row.get("title") or "Untitled"))
        shared = html.escape(str(row.get("shared_text") or ""))
        notes = html.escape(str(row.get("notes") or ""))
        created = html.escape(str(row.get("created_at") or "")[:10])
        link = _safe_link(str(row.get("source_url") or ""))
        cards.append('<article style="padding:14px;margin:10px 0;'
                     'border:1px solid #64748b55;border-radius:12px;overflow-wrap:anywhere">'
                     f'<strong>💡 {title}</strong>'
                     f'<div style="opacity:.7;font-size:.85em;margin-top:4px">Saved {created}</div>'
                     + link
                     + (f'<p style="white-space:pre-wrap">{shared}</p>' if shared else "")
                     + (f'<p style="white-space:pre-wrap"><b>Notes:</b> {notes}</p>' if notes else "")
                     + '</article>')
    return "\n".join(cards)

def _load(client, user_id):
    response = (client.table(TABLE)
                .select("id,title,source_url,shared_text,notes,created_at")
                .eq("user_id", user_id).order("created_at", desc=True)
                .limit(200).execute())
    rows = response.data or []
    choices = [(str(row.get("title") or "Untitled")[:80], str(row["id"])) for row in rows]
    return _render_ideas(rows), gr.update(choices=choices, value=None)

def refresh_ideas(saved_session):
    try:
        client, user_id, updated = _authenticated_client(saved_session)
        listing, choices = _load(client, user_id)
        return listing, choices, "✅ Inbox refreshed.", updated
    except ValueError as exc:
        return "", gr.update(choices=[], value=None), str(exc), empty_saved_session()
    except Exception as exc:
        print("Ideas inbox refresh error:", type(exc).__name__, str(exc))
        return "", gr.update(choices=[], value=None), "❌ Could not load ideas right now.", saved_session

def save_idea(title, source_url, shared_text, notes, saved_session):
    title = (title or "").strip()
    source_url = (source_url or "").strip()
    shared_text = (shared_text or "").strip()
    notes = (notes or "").strip()
    if not title:
        return "❌ Enter a title for your idea.", gr.update(), gr.update(), saved_session
    if not (source_url or shared_text or notes):
        return "❌ Add a link, shared text, or notes.", gr.update(), gr.update(), saved_session
    if len(title) > 200 or len(source_url) > 2000 or len(shared_text) > 10000 or len(notes) > 5000:
        return "❌ Please shorten your idea.", gr.update(), gr.update(), saved_session
    if source_url:
        parsed = urlsplit(source_url)
        if parsed.scheme.lower() not in ("http", "https") or not parsed.netloc:
            return "❌ Link must begin with https:// or http://.", gr.update(), gr.update(), saved_session
    try:
        client, user_id, updated = _authenticated_client(saved_session)
        client.table(TABLE).insert({"user_id": user_id, "title": title,
                                   "source_url": source_url, "shared_text": shared_text,
                                   "notes": notes}).execute()
        listing, choices = _load(client, user_id)
        return "✅ Idea saved to your inbox!", listing, choices, updated
    except ValueError as exc:
        return str(exc), gr.update(), gr.update(), empty_saved_session()
    except Exception as exc:
        print("Ideas inbox save error:", type(exc).__name__, str(exc))
        return "❌ Couldn't save your idea. Please try again.", gr.update(), gr.update(), saved_session

def delete_idea(idea_id, saved_session):
    if not idea_id:
        return "Choose an idea to delete.", gr.update(), gr.update(), saved_session
    try:
        client, user_id, updated = _authenticated_client(saved_session)
        (client.table(TABLE).delete().eq("id", str(idea_id))
         .eq("user_id", user_id).execute())
        listing, choices = _load(client, user_id)
        return "✅ Idea deleted.", listing, choices, updated
    except ValueError as exc:
        return str(exc), gr.update(), gr.update(), empty_saved_session()
    except Exception as exc:
        print("Ideas inbox delete error:", type(exc).__name__, str(exc))
        return "❌ Couldn't delete the idea.", gr.update(), gr.update(), saved_session

def build_ideas_inbox_page(saved_login, visible=False):
    with gr.Column(visible=visible, elem_id="cc-ideas-inbox") as page:
        gr.Markdown("## 💡 Content Ideas Inbox\nSave inspiration here first. You can schedule it later.")
        idea_title = gr.Textbox(label="Idea Title", placeholder="Example: Zelda challenge video")
        idea_link = gr.Textbox(label="Source Link (optional)", placeholder="https://...")
        idea_text = gr.Textbox(label="Shared Text (optional)", lines=3)
        idea_notes = gr.Textbox(label="Your Notes (optional)", lines=3)
        save_button = gr.Button("💾 Save Idea", variant="primary")
        status = gr.Markdown("")
        gr.Markdown("### Saved Ideas")
        refresh_button = gr.Button("🔄 Refresh Inbox")
        listing = gr.HTML('<div style="padding:16px">Open the inbox to load your saved ideas.</div>')
        delete_picker = gr.Dropdown(choices=[], label="Choose an idea to delete", value=None)
        delete_button = gr.Button("🗑️ Delete Selected Idea")
        save_button.click(save_idea, inputs=[idea_title, idea_link, idea_text, idea_notes, saved_login],
                          outputs=[status, listing, delete_picker, saved_login], show_progress="minimal")
        refresh_button.click(refresh_ideas, inputs=[saved_login],
                             outputs=[listing, delete_picker, status, saved_login], show_progress="minimal")
        delete_button.click(delete_idea, inputs=[delete_picker, saved_login],
                            outputs=[status, listing, delete_picker, saved_login], show_progress="minimal")
    return page, (listing, delete_picker, status, idea_title, idea_link, idea_text)

