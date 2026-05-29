import os
import base64
import cv2
import requests
import gradio as gr
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
# ELEVENLABS_API_KEY

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Orbitron:wght@600;700;800;900&display=swap');

:root {
    --cc-black: #05030d;
    --cc-deep: #0b0620;
    --cc-panel: rgba(13, 9, 35, 0.92);
    --cc-panel2: rgba(23, 13, 55, 0.92);
    --cc-purple: #9d4edd;
    --cc-pink: #ff2bd6;
    --cc-cyan: #00e5ff;
    --cc-blue: #4d96ff;
    --cc-orange: #ff8c1a;
    --cc-text: #ffffff;
    --cc-muted: #d8d6ff;
}

html, body, .gradio-container {
    min-height: 100vh !important;
    color: var(--cc-text) !important;
    font-family: 'Inter', system-ui, sans-serif !important;
    background:
        linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px),
        radial-gradient(circle at 18% 8%, rgba(255, 43, 214, 0.36), transparent 28%),
        radial-gradient(circle at 86% 15%, rgba(0, 229, 255, 0.30), transparent 26%),
        radial-gradient(circle at 50% 105%, rgba(157, 78, 221, 0.42), transparent 40%),
        linear-gradient(135deg, #05030d 0%, #0b0620 40%, #17072b 100%) !important;
    background-size: 42px 42px, 42px 42px, auto, auto, auto, auto !important;
}

.gradio-container {
    max-width: 1280px !important;
    margin: auto !important;
    padding: 26px !important;
}

.gradio-container::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    background: repeating-linear-gradient(
        to bottom,
        rgba(255,255,255,0.035) 0px,
        rgba(255,255,255,0.035) 1px,
        transparent 2px,
        transparent 5px
    );
    opacity: .18;
    z-index: 9999;
}

#channel-coach-header {
    position: relative;
    overflow: hidden;
    padding: 34px 32px !important;
    border-radius: 28px !important;
    border: 2px solid rgba(0, 229, 255, 0.55) !important;
    background:
        linear-gradient(135deg, rgba(255,43,214,0.20), rgba(0,229,255,0.11)),
        rgba(8, 5, 24, 0.92) !important;
    box-shadow:
        0 0 18px rgba(0,229,255,.55),
        0 0 42px rgba(255,43,214,.28),
        inset 0 0 40px rgba(157,78,221,.18) !important;
    margin-bottom: 22px !important;
}

#channel-coach-header::after {
    content: "CREATOR MODE";
    position: absolute;
    right: 26px;
    top: 22px;
    font-family: 'Orbitron', sans-serif;
    letter-spacing: .18em;
    font-size: .72rem;
    color: var(--cc-cyan);
    text-shadow: 0 0 12px var(--cc-cyan);
    opacity: .85;
}

#channel-coach-header h1 {
    font-family: 'Orbitron', sans-serif !important;
    text-transform: uppercase;
    letter-spacing: .04em;
    font-size: clamp(2rem, 4vw, 4rem) !important;
    line-height: 1.05 !important;
    margin: 0 0 14px 0 !important;
    background: linear-gradient(90deg, #ffffff, var(--cc-cyan), var(--cc-pink), #fff) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    text-shadow: 0 0 26px rgba(0,229,255,.65) !important;
}

#channel-coach-header p {
    color: var(--cc-muted) !important;
    font-size: 1.08rem !important;
    max-width: 900px !important;
}

/* Tabs */
.tabs, .tab-nav {
    border-radius: 22px !important;
    background: rgba(5, 3, 13, .74) !important;
    border: 1px solid rgba(255,43,214,.32) !important;
    box-shadow: 0 0 22px rgba(157,78,221,.22) !important;
    padding: 6px !important;
}

button[role='tab'] {
    border-radius: 16px !important;
    color: #f2eaff !important;
    background: rgba(16, 10, 43, .78) !important;
    border: 1px solid rgba(0,229,255,.20) !important;
    font-weight: 800 !important;
    box-shadow: inset 0 0 14px rgba(0,229,255,.05) !important;
}

button[role='tab'][aria-selected='true'] {
    color: #05030d !important;
    background: linear-gradient(90deg, var(--cc-cyan), var(--cc-pink)) !important;
    border: 1px solid rgba(255,255,255,.7) !important;
    box-shadow: 0 0 18px rgba(0,229,255,.75), 0 0 24px rgba(255,43,214,.35) !important;
}

/* Cards / panels */
.block, .gr-box, .form, .panel, .gr-panel, .tabitem, [role='tabpanel'] {
    background: linear-gradient(180deg, var(--cc-panel2), var(--cc-panel)) !important;
    border: 1px solid rgba(0,229,255,.35) !important;
    border-radius: 22px !important;
    box-shadow: 0 0 24px rgba(0,229,255,.12), 0 18px 60px rgba(0,0,0,.46) !important;
}

label, .block-label, .gr-form label, .label-wrap span {
    color: #ffffff !important;
    font-weight: 900 !important;
    letter-spacing: .02em !important;
    text-shadow: 0 0 10px rgba(0,229,255,.55) !important;
}

textarea, input, select, .wrap, .container, .secondary-wrap {
    background: rgba(2, 2, 12, .78) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,43,214,.38) !important;
    border-radius: 18px !important;
    box-shadow: inset 0 0 18px rgba(0,229,255,.08) !important;
}

textarea:focus, input:focus {
    border-color: var(--cc-cyan) !important;
    box-shadow: 0 0 0 3px rgba(0,229,255,.18), 0 0 24px rgba(0,229,255,.30) !important;
}

/* Main buttons */
button, .gr-button, button.primary {
    border-radius: 18px !important;
    border: 1px solid rgba(255,255,255,.62) !important;
    background: linear-gradient(90deg, var(--cc-pink), var(--cc-purple), var(--cc-cyan)) !important;
    color: #ffffff !important;
    font-weight: 900 !important;
    letter-spacing: .04em !important;
    text-transform: uppercase !important;
    box-shadow: 0 0 20px rgba(255,43,214,.55), 0 0 35px rgba(0,229,255,.25) !important;
    min-height: 48px !important;
}

button:hover, .gr-button:hover {
    transform: translateY(-2px) scale(1.01) !important;
    filter: brightness(1.18) !important;
    box-shadow: 0 0 28px rgba(255,43,214,.85), 0 0 46px rgba(0,229,255,.42) !important;
}

/* Dropdown text */
.svelte-1gfkn6j, .wrap-inner, .single-select-wrap {
    color: #ffffff !important;
}

/* Outputs */
.output-class, .prose, .markdown, .gr-markdown {
    color: #ffffff !important;
}

.footer, footer { display: none !important; }
"""

# =========================
# VOICES
# =========================

VOICE_OPTIONS = {
    "Rachel": "21m00Tcm4TlvDq8ikWAM",
    "Bella": "EXAVITQu4vr4xnSDxMaL",
    "Antoni": "ErXwobaYiN019PkySvjV",
    "Josh": "TxGEqnHWrfWFTfGW9XjX",
}

# =========================
# OPENAI TEXT HELPER
# =========================

def ask_channel_coach(prompt):
    if not os.getenv("OPENAI_API_KEY"):
        return "Missing OPENAI_API_KEY. Add your OpenAI API key to your environment variables."

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


def comment_assistant(comment, tone):
    prompt = f"""
Write 5 replies to this viewer comment.

Comment: {comment}
Tone: {tone}
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
                        "text": """
You are Channel Coach, a YouTube thumbnail expert.

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
# VOICEOVER
# =========================

def generate_voice(script, voice_name):
    if not script.strip():
        return None

    if not ELEVENLABS_API_KEY:
        print("Missing ELEVENLABS_API_KEY.")
        return None

    voice_id = VOICE_OPTIONS[voice_name]

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "text": script,
        "model_id": "eleven_monolingual_v1"
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code != 200:
        print(response.text)
        return None

    output_path = "voice.mp3"

    with open(output_path, "wb") as f:
        f.write(response.content)

    return output_path


# =========================
# GRADIO APP
# =========================

with gr.Blocks(title="Channel Coach", head=custom_head, css=custom_css) as app:

    gr.Markdown(
        """
        # 🎬 Channel Coach
        Neon-powered creator tools for titles, SEO, video reviews, Shorts, thumbnails, comments, and voiceovers.
        """,
        elem_id="channel-coach-header"
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

    with gr.Tab("Comment Assistant"):
        comment_input = gr.Textbox(label="Viewer Comment", lines=4)
        comment_tone = gr.Dropdown(
            ["Friendly", "Funny", "Supportive", "Professional", "Bold"],
            value="Friendly",
            label="Tone"
        )
        comment_button = gr.Button("Write Replies")
        comment_output = gr.Textbox(label="Reply Options", lines=10)

        comment_button.click(
            comment_assistant,
            inputs=[comment_input, comment_tone],
            outputs=comment_output
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

    with gr.Tab("AI Voiceover"):
        script_input = gr.Textbox(label="Voiceover Script", lines=8)
        voice_dropdown = gr.Dropdown(
            choices=list(VOICE_OPTIONS.keys()),
            value="Bella",
            label="Choose Voice"
        )
        voice_button = gr.Button("Generate Voiceover")
        voice_output = gr.Audio(label="Generated Voiceover")

        voice_button.click(
            generate_voice,
            inputs=[script_input, voice_dropdown],
            outputs=voice_output
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



      




 











  

 

 
 


      
      

  

   
 
  
