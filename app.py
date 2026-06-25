import os
import json
import base64
import uuid
import calendar
import html
import cv2
import gradio as gr
from datetime import date, datetime
from dotenv import load_dotenv
from openai import OpenAI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

load_dotenv()

# =========================
# API KEYS
# =========================
# IMPORTANT:
# Do NOT paste your real API keys directly into this file.
# Put them in your environment variables instead:
# OPENAI_API_KEY

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# =========================
# CREATOR PROFILE MEMORY
# =========================
# This saves the creator's niche, goals, style, and channel details so every
# Channel Coach tool can give personalized advice instead of generic feedback.
#
# On Render, set CREATOR_PROFILE_FILE to a path on a persistent disk if you want
# the profile to survive redeploys/restarts. Example:
# CREATOR_PROFILE_FILE=/data/creator_profile.json

PROFILE_FILE = os.getenv("CREATOR_PROFILE_FILE", "creator_profile.json")

DEFAULT_PROFILE = {
    "channel_name": "",
    "creator_name": "",
    "niche": "",
    "target_audience": "",
    "content_style": "",
    "current_games": "",
    "main_platforms": "",
    "goals": "",
    "preferred_tone": "",
    "things_to_avoid": ""
}


def load_creator_profile():
    try:
        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                saved_profile = json.load(f)

            profile = DEFAULT_PROFILE.copy()
            profile.update(saved_profile)
            return profile

    except Exception:
        # If the saved profile file ever gets corrupted, the app will still load.
        return DEFAULT_PROFILE.copy()

    return DEFAULT_PROFILE.copy()

def save_creator_profile(
    channel_name,
    creator_name,
    niche,
    target_audience,
    content_style,
    current_games,
    main_platforms,
    goals,
    preferred_tone,
    things_to_avoid
):
    profile = {
        "channel_name": channel_name,
        "creator_name": creator_name,
        "niche": niche,
        "target_audience": target_audience,
        "content_style": content_style,
        "current_games": current_games,
        "main_platforms": main_platforms,
        "goals": goals,
        "preferred_tone": preferred_tone,
        "things_to_avoid": things_to_avoid
    }

    try:
        profile_dir = os.path.dirname(PROFILE_FILE)
        if profile_dir:
            os.makedirs(profile_dir, exist_ok=True)

        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=4)

        return "✅ Creator profile saved! Channel Coach will use this profile in titles, SEO, descriptions, reviews, Shorts ideas, and thumbnail feedback."

    except Exception as e:
        return f"❌ Could not save creator profile: {e}"


def creator_profile_context():
    profile = load_creator_profile()

    return f"""
Creator Profile Memory:
- Channel name: {profile.get("channel_name", "")}
- Creator name: {profile.get("creator_name", "")}
- Niche: {profile.get("niche", "")}
- Target audience: {profile.get("target_audience", "")}
- Content style: {profile.get("content_style", "")}
- Current games/content: {profile.get("current_games", "")}
- Main platforms: {profile.get("main_platforms", "")}
- Goals: {profile.get("goals", "")}
- Preferred coaching tone: {profile.get("preferred_tone", "")}
- Things to avoid: {profile.get("things_to_avoid", "")}

Use this creator profile in your answer. Be specific to this creator whenever possible.
"""


# =========================
# CONTENT CALENDAR
# =========================
# On Render, set CONTENT_CALENDAR_FILE to a path on a persistent disk if you want
# the calendar to survive redeploys/restarts. Example:
# CONTENT_CALENDAR_FILE=/data/content_calendar.json

CONTENT_CALENDAR_FILE = os.getenv("CONTENT_CALENDAR_FILE", "content_calendar.json")

CONTENT_STATUSES = [
    "Idea",
    "Script",
    "Recording",
    "Editing",
    "Thumbnail",
    "Scheduled",
    "Published"
]

CONTENT_TYPES = [
    "Long Video",
    "Short",
    "Livestream",
    "Community Post"
]


def load_content_calendar():
    try:
        if os.path.exists(CONTENT_CALENDAR_FILE):
            with open(CONTENT_CALENDAR_FILE, "r", encoding="utf-8") as f:
                items = json.load(f)

            if isinstance(items, list):
                return items
    except Exception:
        return []

    return []


def save_content_calendar(items):
    calendar_dir = os.path.dirname(CONTENT_CALENDAR_FILE)
    if calendar_dir:
        os.makedirs(calendar_dir, exist_ok=True)

    with open(CONTENT_CALENDAR_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=4)


def validate_calendar_date(date_text):
    try:
        return datetime.strptime(date_text.strip(), "%Y-%m-%d").date()
    except Exception:
        return None


def item_label(item):
    return f'{item.get("publish_date", "No date")} | {item.get("status", "")} | {item.get("title", "Untitled")}'


def get_calendar_choices():
    items = sorted(load_content_calendar(), key=lambda x: x.get("publish_date", "9999-12-31"))
    return [(item_label(item), item.get("id")) for item in items]


def add_content_item(title, content_type, game_topic, status, publish_date, notes, month, year, status_filter, type_filter):
    if not title or not title.strip():
        return (
            render_content_calendar(month, year, status_filter, type_filter),
            gr.update(choices=get_calendar_choices()),
            "❌ Please enter a title."
        )

    parsed_date = validate_calendar_date(publish_date or "")
    if parsed_date is None:
        return (
            render_content_calendar(month, year, status_filter, type_filter),
            gr.update(choices=get_calendar_choices()),
            "❌ Please enter the date like this: YYYY-MM-DD"
        )

    items = load_content_calendar()
    items.append({
        "id": str(uuid.uuid4()),
        "title": title.strip(),
        "content_type": content_type,
        "game_topic": (game_topic or "").strip(),
        "status": status,
        "publish_date": parsed_date.isoformat(),
        "notes": (notes or "").strip(),
        "created_at": datetime.now().isoformat()
    })

    save_content_calendar(items)

    return (
        render_content_calendar(month, year, status_filter, type_filter),
        gr.update(choices=get_calendar_choices()),
        "✅ Added to your content calendar!"
    )


def render_content_calendar(month=None, year=None, status_filter="All", type_filter="All"):
    today = date.today()

    try:
        month = int(month or today.month)
        year = int(year or today.year)
    except Exception:
        month = today.month
        year = today.year

    items = load_content_calendar()

    if status_filter != "All":
        items = [item for item in items if item.get("status") == status_filter]

    if type_filter != "All":
        items = [item for item in items if item.get("content_type") == type_filter]

    cal = calendar.Calendar(firstweekday=6)
    weeks = cal.monthdatescalendar(year, month)

    type_emoji = {
        "Long Video": "🎮",
        "Short": "📱",
        "Livestream": "🔴",
        "Community Post": "💬"
    }

    status_class = {
        "Idea": "status-idea",
        "Script": "status-script",
        "Recording": "status-recording",
        "Editing": "status-editing",
        "Thumbnail": "status-thumbnail",
        "Scheduled": "status-scheduled",
        "Published": "status-published"
    }

    html_output = f"""
    <div class="cc-calendar-wrap">
        <h2>{html.escape(calendar.month_name[month])} {year}</h2>
        <div class="cc-calendar-grid cc-calendar-header">
    """

    for day_name in ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]:
        html_output += f'<div class="cc-day-name">{day_name}</div>'

    html_output += "</div><div class=\"cc-calendar-grid\">"

    for week in weeks:
        for day in week:
            muted = " cc-muted" if day.month != month else ""
            today_class = " cc-today" if day == today else ""

            html_output += f"""
            <div class="cc-calendar-day{muted}{today_class}">
                <div class="cc-day-number">{day.day}</div>
            """

            day_items = [item for item in items if item.get("publish_date") == day.isoformat()]

            for item in day_items:
                content_type = item.get("content_type", "Long Video")
                status = item.get("status", "Idea")
                emoji = type_emoji.get(content_type, "🎬")
                css_class = status_class.get(status, "status-idea")

                title = html.escape(item.get("title", "Untitled"))
                game_topic = html.escape(item.get("game_topic", ""))
                notes = html.escape(item.get("notes", ""))

                html_output += f"""
                <div class="cc-content-card {css_class}" title="{notes}">
                    <div class="cc-card-title">{emoji} {title}</div>
                    <div class="cc-card-meta">{html.escape(status)} · {html.escape(content_type)}</div>
                    <div class="cc-card-topic">{game_topic}</div>
                </div>
                """

            html_output += "</div>"

    html_output += """
        </div>
    </div>
    """

    return html_output


def refresh_content_calendar(month, year, status_filter, type_filter):
    return render_content_calendar(month, year, status_filter, type_filter)


def load_selected_content_item(selected_item_id):
    if not selected_item_id:
        return "", "Long Video", "", "Idea", date.today().isoformat(), "", "Choose an item to edit."

    items = load_content_calendar()
    for item in items:
        if item.get("id") == selected_item_id:
            return (
                item.get("title", ""),
                item.get("content_type", "Long Video"),
                item.get("game_topic", ""),
                item.get("status", "Idea"),
                item.get("publish_date", date.today().isoformat()),
                item.get("notes", ""),
                "Loaded item. Make changes, then click Save Edit."
            )

    return "", "Long Video", "", "Idea", date.today().isoformat(), "", "Could not find that calendar item."


def update_content_item(selected_item_id, title, content_type, game_topic, status, publish_date, notes, month, year, status_filter, type_filter):
    if not selected_item_id:
        return (
            render_content_calendar(month, year, status_filter, type_filter),
            gr.update(choices=get_calendar_choices()),
            "❌ Choose an item to edit first."
        )

    parsed_date = validate_calendar_date(publish_date or "")
    if parsed_date is None:
        return (
            render_content_calendar(month, year, status_filter, type_filter),
            gr.update(choices=get_calendar_choices()),
            "❌ Please enter the date like this: YYYY-MM-DD"
        )

    items = load_content_calendar()
    updated = False

    for item in items:
        if item.get("id") == selected_item_id:
            item.update({
                "title": (title or "Untitled").strip(),
                "content_type": content_type,
                "game_topic": (game_topic or "").strip(),
                "status": status,
                "publish_date": parsed_date.isoformat(),
                "notes": (notes or "").strip(),
                "updated_at": datetime.now().isoformat()
            })
            updated = True
            break

    save_content_calendar(items)

    if updated:
        message = "✅ Calendar item updated."
    else:
        message = "❌ Could not find that calendar item."

    return (
        render_content_calendar(month, year, status_filter, type_filter),
        gr.update(choices=get_calendar_choices(), value=selected_item_id),
        message
    )


def delete_content_item(selected_item_id, month, year, status_filter, type_filter):
    if not selected_item_id:
        return (
            render_content_calendar(month, year, status_filter, type_filter),
            gr.update(choices=get_calendar_choices()),
            "❌ Choose an item to delete first."
        )

    items = load_content_calendar()
    new_items = [item for item in items if item.get("id") != selected_item_id]
    save_content_calendar(new_items)

    return (
        render_content_calendar(month, year, status_filter, type_filter),
        gr.update(choices=get_calendar_choices(), value=None),
        "🗑️ Calendar item deleted."
    )


# =========================
# PWA / APP-LIKE SETTINGS
# =========================

custom_head = """
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#111111">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Channel Coach">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<script>
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/service-worker.js')
            .then(function(registration) {
                console.log('Channel Coach service worker registered:', registration.scope);
            })
            .catch(function(error) {
                console.log('Channel Coach service worker failed:', error);
            });
    });
}
</script>
"""


# =========================
# CHANNEL COACH NEON / RETRO STYLE
# =========================
# Big 80s synthwave/arcade style update.

custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #0f1117;
    --bg2: #171923;
    --panel: #1e2230;
    --panel2: #252b3b;
    --border: #31384d;
    --accent: #8b5cf6;
    --accent2: #22d3ee;
    --text: #f5f7ff;
    --muted: #b8c0d9;
}

html, body, .gradio-container {
    min-height: 100vh !important;
    background:
        radial-gradient(circle at top left, rgba(139,92,246,.12), transparent 25%),
        radial-gradient(circle at top right, rgba(34,211,238,.10), transparent 22%),
        linear-gradient(180deg, var(--bg) 0%, #0b0d12 100%) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
}

.gradio-container {
    width: 100% !important;
    max-width: 1200px !important;
    margin: 0 auto !important;
    padding: 20px !important;
    box-sizing: border-box !important;
}

#channel-coach-header {
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
    background: linear-gradient(135deg, #1f2433, #171b27) !important;
    border: 1px solid var(--border) !important;
    border-radius: 20px !important;
    padding: 28px !important;
    margin-bottom: 20px !important;
    box-shadow: 0 10px 30px rgba(0,0,0,.35) !important;
}

#channel-coach-header h1 {
    font-size: 3rem !important;
    margin-bottom: 10px !important;
    color: var(--text) !important;
    letter-spacing: -.03em !important;
}

#channel-coach-header p {
    color: var(--muted) !important;
    font-size: 1rem !important;
}

/* Mobile layout fixes */
@media (max-width: 768px) {
    html, body {
        width: 100% !important;
        overflow-x: hidden !important;
    }

    .gradio-container {
        width: 100% !important;
        max-width: 100% !important;
        padding: 10px !important;
        margin: 0 !important;
        box-sizing: border-box !important;
    }

    #channel-coach-header {
        width: 100% !important;
        max-width: calc(100vw - 20px) !important;
        padding: 14px !important;
        margin: 0 0 12px 0 !important;
        border-radius: 14px !important;
        box-sizing: border-box !important;
    }

    #channel-coach-header h1 {
        font-size: 1.75rem !important;
        line-height: 1.05 !important;
        margin-bottom: 6px !important;
        word-break: normal !important;
    }

    #channel-coach-header p {
        font-size: 0.8rem !important;
        line-height: 1.35 !important;
        margin-bottom: 0 !important;
    }

    .block, .gr-box, .form, .panel, .gr-panel, .tabitem, [role='tabpanel'] {
        max-width: 100% !important;
        box-sizing: border-box !important;
    }

    textarea, input, select {
        max-width: 100% !important;
        box-sizing: border-box !important;
    }
}

.tabs, .tab-nav {
    background: transparent !important;
    border: none !important;
}

button[role='tab'] {
    background: var(--panel) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--muted) !important;
    font-weight: 600 !important;
}

button[role='tab'][aria-selected='true'] {
    background: linear-gradient(90deg, var(--accent), var(--accent2)) !important;
    color: white !important;
    border: none !important;
}

.block, .gr-box, .form, .panel, .gr-panel, .tabitem, [role='tabpanel'] {
    background: linear-gradient(180deg, var(--panel2), var(--panel)) !important;
    border: 1px solid var(--border) !important;
    border-radius: 18px !important;
    box-shadow: 0 8px 24px rgba(0,0,0,.25) !important;
}

textarea, input, select {
    background: #121521 !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}

textarea:focus, input:focus {
    border-color: var(--accent2) !important;
    box-shadow: 0 0 0 3px rgba(34,211,238,.15) !important;
}

button, .gr-button, button.primary {
    background: linear-gradient(90deg, var(--accent), var(--accent2)) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
}

button:hover, .gr-button:hover {
    filter: brightness(1.08) !important;
    transform: translateY(-1px);
}

label, .block-label {
    color: var(--text) !important;
    font-weight: 600 !important;
}

.footer, footer {
    display: none !important;
}


/* Content Calendar */
.cc-calendar-wrap h2 {
    color: var(--text) !important;
    margin: 10px 0 16px 0 !important;
}

.cc-calendar-grid {
    display: grid;
    grid-template-columns: repeat(7, minmax(0, 1fr));
    gap: 8px;
    width: 100%;
}

.cc-calendar-header {
    margin-bottom: 8px;
}

.cc-day-name {
    color: var(--muted);
    text-align: center;
    font-weight: 800;
    font-size: 0.85rem;
}

.cc-calendar-day {
    min-height: 132px;
    background: #121521;
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 8px;
    box-sizing: border-box;
    overflow: hidden;
}

.cc-calendar-day.cc-muted {
    opacity: 0.35;
}

.cc-calendar-day.cc-today {
    border-color: var(--accent2);
    box-shadow: 0 0 0 2px rgba(34,211,238,.16);
}

.cc-day-number {
    color: var(--text);
    font-weight: 800;
    margin-bottom: 7px;
}

.cc-content-card {
    border-radius: 10px;
    padding: 7px;
    margin-bottom: 6px;
    border-left: 4px solid var(--accent);
    background: rgba(255,255,255,.07);
}

.cc-card-title {
    color: var(--text);
    font-weight: 800;
    font-size: 0.78rem;
    line-height: 1.2;
}

.cc-card-meta, .cc-card-topic {
    color: var(--muted);
    font-size: 0.68rem;
    line-height: 1.25;
}

.status-idea { border-left-color: #a78bfa; }
.status-script { border-left-color: #f472b6; }
.status-recording { border-left-color: #fb923c; }
.status-editing { border-left-color: #22d3ee; }
.status-thumbnail { border-left-color: #facc15; }
.status-scheduled { border-left-color: #60a5fa; }
.status-published { border-left-color: #4ade80; }

@media (max-width: 768px) {
    .cc-calendar-grid {
        grid-template-columns: 1fr !important;
    }

    .cc-calendar-header {
        display: none !important;
    }

    .cc-calendar-day {
        min-height: auto !important;
    }
}

"""

# =========================
# OPENAI TEXT HELPER
# =========================

def ask_channel_coach(prompt, use_profile=True):
    if not os.getenv("OPENAI_API_KEY"):
        return "Missing OPENAI_API_KEY. Add your OpenAI API key to your environment variables."

    if use_profile:
        prompt = creator_profile_context() + "\n\nUser request:\n" + prompt

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )
    return response.output_text


# =========================
# IMAGE / VIDEO HELPERS
# =========================

def encode_image_file(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def extract_video_frames(video_path, max_frames=8):
    frames = []

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        return frames

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if total_frames <= 0:
        cap.release()
        return frames

    frame_positions = []

    for i in range(max_frames):
        position = int((i + 1) * total_frames / (max_frames + 1))
        frame_positions.append(position)

    for position in frame_positions:
        cap.set(cv2.CAP_PROP_POS_FRAMES, position)
        success, frame = cap.read()

        if success:
            success, buffer = cv2.imencode(".jpg", frame)

            if success:
                frame_base64 = base64.b64encode(buffer).decode("utf-8")
                frames.append(frame_base64)

    cap.release()
    return frames


def analyze_video_with_frames(video_file, notes, video_type):
    if video_file is None and not notes.strip():
        return "Please upload a video or paste notes first."

    content = [
        {
            "type": "input_text",
            "text": f"""
You are Channel Coach, an expert YouTube creator coach.

{creator_profile_context()}

Analyze this {video_type}.

Creator notes:
{notes}

You are being shown sample frames extracted from the uploaded video.

Give detailed creator feedback:
- what works visually
- what feels boring or slow
- what should be cut
- pacing advice
- where to add text
- where to add arrows/circles/zoom
- best Shorts moments if this is long-form
- hook strength
- title ideas
- thumbnail ideas
- final score out of 10
"""
        }
    ]

    if video_file is not None:
        frames = extract_video_frames(video_file, max_frames=8)

        if not frames:
            return "I could not extract frames from this video. Try a different video format like MP4."

        for frame in frames:
            content.append(
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{frame}"
                }
            )

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "user",
                "content": content
            }
        ]
    )

    return response.output_text


# =========================
# TEXT TOOLS
# =========================

def generate_titles(video_idea, platform, tone):
    prompt = f"""
You are Channel Coach.

Create 10 catchy titles.

Platform: {platform}
Tone: {tone}
Video idea: {video_idea}

Make them clickable but not fake clickbait.
"""
    return ask_channel_coach(prompt)


def seo_help(video_idea, platform, niche):
    prompt = f"""
You are Channel Coach.

Create SEO help.

Platform: {platform}
Niche: {niche}
Video idea: {video_idea}

Give:
- searchable title
- keywords
- SEO description
- 15 hashtags
- tags
"""
    return ask_channel_coach(prompt)


def description_help(video_idea, platform, niche):
    prompt = f"""
Write a strong video description.

Platform: {platform}
Niche: {niche}
Video idea: {video_idea}

Include:
- hook sentence
- description paragraph
- call to action
- hashtags
"""
    return ask_channel_coach(prompt)


def video_review(video_file, notes):
    return analyze_video_with_frames(video_file, notes, "long-form YouTube video")


def shorts_review(shorts_file, notes):
    return analyze_video_with_frames(shorts_file, notes, "Short, Reel, or TikTok")


def shorts_ideas(niche, topic):
    prompt = f"""
Create 10 Shorts ideas.

Niche: {niche}
Topic/game: {topic}

For each idea include:
- title
- hook
- on-screen text
- footage idea
- caption
"""
    return ask_channel_coach(prompt)


# =========================
# THUMBNAIL ANALYZER
# =========================

def analyze_thumbnail(image):
    if image is None:
        return "Please upload a thumbnail."

    base64_image = encode_image_file(image)

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"""
You are Channel Coach, a YouTube thumbnail expert.

{creator_profile_context()}

Analyze this thumbnail.

Give:
- first impression
- readability
- visual focus
- clickability
- what works
- what fails
- how to improve it
- 5 better thumbnail text ideas
"""
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{base64_image}"
                    }
                ]
            }
        ]
    )

    return response.output_text


# =========================
# GRADIO APP
# =========================

with gr.Blocks(title="Channel Coach", head=custom_head, css=custom_css) as app:

    gr.Markdown(
        """
        # 🎬 Channel Coach
        AI creator tools for titles, SEO, thumbnails, Shorts, and video reviews.
        """,
        elem_id="channel-coach-header"
    )

    saved_profile = load_creator_profile()

    with gr.Tab("Creator Profile"):
        gr.Markdown(
            """
            ## 🧠 Creator Profile Memory
            Save your channel niche, goals, style, and current content here.
            Channel Coach will use this information in every tool.
            """
        )

        profile_channel_name = gr.Textbox(
            label="Channel Name",
            value=saved_profile.get("channel_name", ""),
            placeholder="Example: My Awesome Gaming Channel"
        )
        profile_creator_name = gr.Textbox(
            label="Creator Name",
            value=saved_profile.get("creator_name", ""),
            placeholder="Example: Nicole, Alex, Gamer Mom, etc."
        )
        profile_niche = gr.Textbox(
            label="Niche",
            value=saved_profile.get("niche", ""),
            placeholder="Example: Retro gaming, cooking, travel, tech reviews...",
            lines=3
        )
        profile_target_audience = gr.Textbox(
            label="Target Audience",
            value=saved_profile.get("target_audience", ""),
            placeholder="Example: Beginners, cozy gamers, busy parents, tech newbies...",
            lines=3
        )
        profile_content_style = gr.Textbox(
            label="Content Style",
            value=saved_profile.get("content_style", ""),
            placeholder="Example: Funny, helpful, cozy, direct, chaotic-good, cinematic...",
            lines=3
        )
        profile_current_games = gr.Textbox(
            label="Current Games / Current Content",
            value=saved_profile.get("current_games", ""),
            placeholder="Example: Stardew Valley guides, Zelda walkthroughs, budget recipes...",
            lines=3
        )
        profile_main_platforms = gr.Textbox(
            label="Main Platforms",
            value=saved_profile.get("main_platforms", ""),
            placeholder="Example: YouTube, TikTok, Instagram Reels, Facebook Reels"
        )
        profile_goals = gr.Textbox(
            label="Goals",
            value=saved_profile.get("goals", ""),
            placeholder="Example: Grow subscribers, improve thumbnails, post 3 Shorts a week...",
            lines=3
        )
        profile_preferred_tone = gr.Textbox(
            label="Preferred Coaching Tone",
            value=saved_profile.get("preferred_tone", ""),
            placeholder="Example: Friendly, honest, motivating, not too corporate...",
            lines=3
        )
        profile_things_to_avoid = gr.Textbox(
            label="Things Channel Coach Should Avoid",
            value=saved_profile.get("things_to_avoid", ""),
            placeholder="Example: Fake clickbait, generic advice, too much jargon...",
            lines=3
        )

        profile_save_button = gr.Button("Save Creator Profile")
        profile_save_status = gr.Textbox(label="Save Status", lines=2)

        profile_save_button.click(
            save_creator_profile,
            inputs=[
                profile_channel_name,
                profile_creator_name,
                profile_niche,
                profile_target_audience,
                profile_content_style,
                profile_current_games,
                profile_main_platforms,
                profile_goals,
                profile_preferred_tone,
                profile_things_to_avoid
            ],
            outputs=profile_save_status
        )


    with gr.Tab("Content Calendar"):
        gr.Markdown(
            """
            ## 📅 Content Calendar
            Plan your long videos, Shorts, livestreams, and community posts.

            Date format: **YYYY-MM-DD**. Example: **2026-06-28**
            """
        )

        with gr.Row():
            with gr.Column(scale=1):
                calendar_title = gr.Textbox(
                    label="Title",
                    placeholder="Example: Getting the Ice Rod"
                )
                calendar_content_type = gr.Dropdown(
                    CONTENT_TYPES,
                    value="Long Video",
                    label="Content Type"
                )
                calendar_game_topic = gr.Textbox(
                    label="Game / Topic",
                    placeholder="Example: Zelda ALTTP"
                )
                calendar_status = gr.Dropdown(
                    CONTENT_STATUSES,
                    value="Idea",
                    label="Status"
                )
                calendar_publish_date = gr.Textbox(
                    label="Target Publish Date",
                    value=date.today().isoformat(),
                    placeholder="YYYY-MM-DD"
                )
                calendar_notes = gr.Textbox(
                    label="Notes",
                    lines=4,
                    placeholder="Example: Need thumbnail, voiceover, and final export."
                )

                calendar_add_button = gr.Button("Add to Calendar")
                calendar_message = gr.Textbox(label="Calendar Status", lines=2)

            with gr.Column(scale=2):
                with gr.Row():
                    calendar_month = gr.Dropdown(
                        choices=list(range(1, 13)),
                        value=date.today().month,
                        label="Month"
                    )
                    calendar_year = gr.Number(
                        value=date.today().year,
                        label="Year",
                        precision=0
                    )

                with gr.Row():
                    calendar_status_filter = gr.Dropdown(
                        ["All"] + CONTENT_STATUSES,
                        value="All",
                        label="Status Filter"
                    )
                    calendar_type_filter = gr.Dropdown(
                        ["All"] + CONTENT_TYPES,
                        value="All",
                        label="Type Filter"
                    )

                calendar_output = gr.HTML(value=render_content_calendar())
                calendar_refresh_button = gr.Button("Refresh Calendar")

        gr.Markdown("### Edit or Delete Calendar Item")

        calendar_item_picker = gr.Dropdown(
            choices=get_calendar_choices(),
            label="Choose Calendar Item"
        )

        calendar_load_button = gr.Button("Load Selected Item")

        with gr.Row():
            calendar_update_button = gr.Button("Save Edit")
            calendar_delete_button = gr.Button("Delete Selected Item")

        calendar_add_button.click(
            add_content_item,
            inputs=[
                calendar_title,
                calendar_content_type,
                calendar_game_topic,
                calendar_status,
                calendar_publish_date,
                calendar_notes,
                calendar_month,
                calendar_year,
                calendar_status_filter,
                calendar_type_filter
            ],
            outputs=[calendar_output, calendar_item_picker, calendar_message]
        )

        calendar_refresh_button.click(
            refresh_content_calendar,
            inputs=[calendar_month, calendar_year, calendar_status_filter, calendar_type_filter],
            outputs=calendar_output
        )

        calendar_month.change(
            refresh_content_calendar,
            inputs=[calendar_month, calendar_year, calendar_status_filter, calendar_type_filter],
            outputs=calendar_output
        )

        calendar_year.change(
            refresh_content_calendar,
            inputs=[calendar_month, calendar_year, calendar_status_filter, calendar_type_filter],
            outputs=calendar_output
        )

        calendar_status_filter.change(
            refresh_content_calendar,
            inputs=[calendar_month, calendar_year, calendar_status_filter, calendar_type_filter],
            outputs=calendar_output
        )

        calendar_type_filter.change(
            refresh_content_calendar,
            inputs=[calendar_month, calendar_year, calendar_status_filter, calendar_type_filter],
            outputs=calendar_output
        )

        calendar_load_button.click(
            load_selected_content_item,
            inputs=calendar_item_picker,
            outputs=[
                calendar_title,
                calendar_content_type,
                calendar_game_topic,
                calendar_status,
                calendar_publish_date,
                calendar_notes,
                calendar_message
            ]
        )

        calendar_update_button.click(
            update_content_item,
            inputs=[
                calendar_item_picker,
                calendar_title,
                calendar_content_type,
                calendar_game_topic,
                calendar_status,
                calendar_publish_date,
                calendar_notes,
                calendar_month,
                calendar_year,
                calendar_status_filter,
                calendar_type_filter
            ],
            outputs=[calendar_output, calendar_item_picker, calendar_message]
        )

        calendar_delete_button.click(
            delete_content_item,
            inputs=[
                calendar_item_picker,
                calendar_month,
                calendar_year,
                calendar_status_filter,
                calendar_type_filter
            ],
            outputs=[calendar_output, calendar_item_picker, calendar_message]
        )


    with gr.Tab("Title Help"):
        title_input = gr.Textbox(label="Video Idea", lines=4)
        title_platform = gr.Dropdown(
            ["YouTube Shorts", "TikTok", "Instagram Reels", "YouTube Long Form"],
            value="YouTube Shorts",
            label="Platform"
        )
        title_tone = gr.Dropdown(
            ["Bold", "Funny", "Friendly", "Casual", "Professional"],
            value="Bold",
            label="Tone"
        )
        title_button = gr.Button("Generate Titles")
        title_output = gr.Textbox(label="Title Ideas", lines=12)

        title_button.click(
            generate_titles,
            inputs=[title_input, title_platform, title_tone],
            outputs=title_output
        )

    with gr.Tab("SEO Help"):
        seo_input = gr.Textbox(label="Video Idea", lines=4)
        seo_platform = gr.Dropdown(
            ["YouTube Shorts", "TikTok", "Instagram Reels", "YouTube Long Form"],
            value="YouTube Shorts",
            label="Platform"
        )
        seo_niche = gr.Textbox(label="Niche", value="Gaming creator")
        seo_button = gr.Button("Generate SEO Help")
        seo_output = gr.Textbox(label="SEO Results", lines=14)

        seo_button.click(
            seo_help,
            inputs=[seo_input, seo_platform, seo_niche],
            outputs=seo_output
        )

    with gr.Tab("Description Help"):
        desc_input = gr.Textbox(label="Video Idea", lines=4)
        desc_platform = gr.Dropdown(
            ["YouTube Shorts", "TikTok", "Instagram Reels", "YouTube Long Form"],
            value="YouTube Shorts",
            label="Platform"
        )
        desc_niche = gr.Textbox(label="Niche", value="Gaming creator")
        desc_button = gr.Button("Write Description")
        desc_output = gr.Textbox(label="Description", lines=14)

        desc_button.click(
            description_help,
            inputs=[desc_input, desc_platform, desc_niche],
            outputs=desc_output
        )

    with gr.Tab("Video Review"):
        video_upload = gr.Video(label="Upload Long-Form Video")
        video_notes = gr.Textbox(label="Optional notes", lines=6)
        video_button = gr.Button("Analyze Video")
        video_output = gr.Textbox(label="Video Feedback", lines=18)

        video_button.click(
            video_review,
            inputs=[video_upload, video_notes],
            outputs=video_output
        )

    with gr.Tab("Shorts Review"):
        shorts_upload = gr.Video(label="Upload Short / Reel / TikTok")
        shorts_notes = gr.Textbox(label="Optional notes", lines=6)
        shorts_button = gr.Button("Analyze Short")
        shorts_output = gr.Textbox(label="Shorts Feedback", lines=18)

        shorts_button.click(
            shorts_review,
            inputs=[shorts_upload, shorts_notes],
            outputs=shorts_output
        )

    with gr.Tab("Shorts Idea Generator"):
        niche_input = gr.Textbox(label="Niche", value="Retro gaming")
        topic_input = gr.Textbox(label="Game or Topic", value="A Link to the Past")
        ideas_button = gr.Button("Generate Shorts Ideas")
        ideas_output = gr.Textbox(label="Shorts Ideas", lines=16)

        ideas_button.click(
            shorts_ideas,
            inputs=[niche_input, topic_input],
            outputs=ideas_output
        )

    with gr.Tab("Thumbnail Analyzer"):
        thumbnail_input = gr.Image(type="filepath", label="Upload Thumbnail")
        thumbnail_button = gr.Button("Analyze Thumbnail")
        thumbnail_output = gr.Textbox(label="Thumbnail Feedback", lines=16)

        thumbnail_button.click(
            analyze_thumbnail,
            inputs=thumbnail_input,
            outputs=thumbnail_output
        )


# =========================
# SERVE PWA FILES
# =========================
# These lines make Gradio serve your app icon files and PWA files.

app.app.mount("/static", StaticFiles(directory="static"), name="static")


@app.app.get("/manifest.json", include_in_schema=False)
async def serve_manifest():
    return FileResponse("manifest.json", media_type="application/manifest+json")


@app.app.get("/service-worker.js", include_in_schema=False)
async def serve_service_worker():
    return FileResponse("service-worker.js", media_type="application/javascript")


port = int(os.environ.get("PORT", 7860))

app.launch(
    server_name="0.0.0.0",
    server_port=port,
    share=False
)
    
