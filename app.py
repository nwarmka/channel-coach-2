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

with gr.Blocks(title="Channel Coach", head=custom_head) as app:

    gr.Markdown("# 🎬 Channel Coach")
    gr.Markdown("AI tools for creators: titles, SEO, video review, Shorts review, thumbnails, comments, and voiceovers.")

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

port = int(os.environ.get("PORT", 7860))

app.launch(
    server_name="0.0.0.0",
    server_port=port,
    head=custom_head
)