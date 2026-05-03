import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
import base64

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

try:
    api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    pass

client = OpenAI(api_key=api_key)

st.set_page_config(
    page_title="Channel Coach",
    page_icon="🎬",
    layout="wide"
)

st.markdown("""
<style>
.main-title {
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 0;
}
.subtitle {
    font-size: 18px;
    color: #666;
    margin-top: 0;
}
.card {
    padding: 20px;
    border-radius: 18px;
    background-color: #f7f7f9;
    border: 1px solid #e6e6e6;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🎬 Channel Coach</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">AI tools for YouTube, TikTok, Shorts, captions, hooks, hashtags, thumbnails, and creator growth.</p>', unsafe_allow_html=True)

st.divider()

st.sidebar.title("⚙️ Creator Settings")

tool = st.sidebar.selectbox(
    "Tool",
    [
        "Content Pack",
        "SEO Caption",
        "Hashtags",
        "Hooks",
        "YouTube Title",
        "TikTok Caption",
        "On-Screen Captions",
        "Thumbnail Text",
        "Thumbnail Analyzer",
        "Script Ideas"
    ]
)

platform = st.sidebar.selectbox(
    "Platform",
    ["YouTube Shorts", "TikTok", "Instagram Reels", "YouTube Long Form"]
)

tone = st.sidebar.selectbox(
    "Tone",
    ["Casual", "Professional", "Funny", "Bold", "Friendly"]
)

niche = st.sidebar.text_input(
    "Niche",
    placeholder="Example: gaming, beauty, fitness"
)

st.sidebar.caption("Built by Nikki | Channel Coach v3")

if "messages" not in st.session_state:
    st.session_state.messages = []

left, right = st.columns([1, 1])

with left:
    st.markdown("### ✍️ Describe Your Content")

    user_text = st.text_area(
        "Video idea, script, comment, thumbnail, or content topic",
        placeholder="Example: A Paper Mario boss fight short where Mario barely wins...",
        height=180
    )

    st.markdown("### 🖼️ Upload Image Optional")

    uploaded_file = st.file_uploader(
        "Upload a thumbnail, screenshot, or video frame",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
        tool = "Thumbnail Analyzer"
        st.success("Image uploaded! Channel Coach will analyze it like a thumbnail or visual post.")

    st.markdown("### 🚀 Quick Tools")

    quick_prompt = None

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎬 Titles", use_container_width=True):
            quick_prompt = "Give me 5 strong video title ideas."

        if st.button("💬 Comment Reply", use_container_width=True):
            quick_prompt = "Help me write a friendly reply to this comment."

    with col2:
        if st.button("📝 Description", use_container_width=True):
            quick_prompt = "Write a YouTube description with hashtags."

        if st.button("⚡ Shorts Ideas", use_container_width=True):
            quick_prompt = "Give me 5 short-form video ideas."

    if st.button("🔥 Viral Captions + SEO Hashtags", use_container_width=True):
        quick_prompt = f"""Create high-performing captions for a {niche} creator on {platform}.

Tone: {tone}

Output:

1. VIRAL HOOK CAPTIONS
- 5 short scroll-stopping hooks

2. ON-SCREEN TEXT
- Break into short readable lines

3. SEO CAPTION
- Keyword-rich but natural

4. HASHTAGS
- 15 hashtags mixing broad, niche, and searchable tags

5. BEST OPTION
- Explain which hook is strongest and why
"""

    if st.button("✨ Generate With Selected Tool", use_container_width=True):
        quick_prompt = user_text

    if uploaded_file and st.button("🖼️ Analyze Uploaded Thumbnail", use_container_width=True):
        quick_prompt = user_text if user_text.strip() else "Analyze this uploaded thumbnail or visual post."

with right:
    st.markdown("### 📌 Current Setup")

    st.markdown(f"""
<div class="card">
<b>Selected Tool:</b> {tool}<br>
<b>Platform:</b> {platform}<br>
<b>Tone:</b> {tone}<br>
<b>Niche:</b> {niche if niche else "Not set yet"}
</div>
""", unsafe_allow_html=True)

    st.info("Tip: Your bot now remembers the conversation, so users can ask follow-ups like “describe that idea in more detail.”")

chat_input = st.chat_input("Ask Channel Coach anything...")

if chat_input:
    quick_prompt = chat_input


def build_prompt(tool, platform, niche, tone, user_request):
    if tool == "Content Pack":
        task = """
Create a full content pack.

Include:
1. Best Title
2. Hook
3. SEO Caption
4. Hashtags
5. On-Screen Text
6. Thumbnail Text
7. Why This Works
"""
    elif tool == "SEO Caption":
        task = "Write a high-performing SEO caption that sounds natural and creator-ready."
    elif tool == "Hashtags":
        task = "Generate 15 hashtags. Mix broad, niche, searchable, and platform-friendly hashtags."
    elif tool == "Hooks":
        task = "Create 5 strong hooks that make people want to keep watching."
    elif tool == "YouTube Title":
        task = "Create 5 clickable YouTube titles that are clear, searchable, and not clickbait."
    elif tool == "TikTok Caption":
        task = "Write 5 TikTok captions that are short, catchy, and engagement-friendly."
    elif tool == "On-Screen Captions":
        task = "Create short, punchy on-screen captions. Keep each line easy to read."
    elif tool == "Thumbnail Text":
        task = "Create 10 bold thumbnail text ideas. Keep each one 3–5 words max."
    elif tool == "Thumbnail Analyzer":
        task = """
Analyze the uploaded thumbnail, screenshot, or visual post.

Include:
1. Overall thumbnail strength
2. What works visually
3. What is weak or unclear
4. Text readability
5. Clickability score from 1–10
6. Better thumbnail text ideas
7. Better title ideas
8. Better hook ideas
9. SEO caption idea
10. Hashtags
"""
    else:
        task = "Generate useful, specific script or content ideas."

    return f"""
You are Channel Coach, an AI content strategist for creators.

Platform: {platform}
Niche: {niche}
Tone: {tone}

User request:
{user_request}

Task:
{task}

Important conversation rules:
- Use the previous conversation when the user asks follow-up questions.
- If the user says things like "describe it more," "make it better," "expand that," or "give me more detail," continue from the previous idea.
- Do not say you need more context if the previous messages already contain the idea.
- Be specific, not generic.
- Use SEO-rich language when helpful.
- Make it catchy but not cringe.
- Give ready-to-copy examples.
- Focus on hooks, retention, discoverability, visuals, and engagement.
"""


if quick_prompt:
    if not quick_prompt.strip() and not uploaded_file:
        st.warning("Please describe your video or upload an image first.")
    else:
        user_message = quick_prompt if quick_prompt else "Analyze the uploaded image."
        st.session_state.messages.append({"role": "user", "content": user_message})

        if "VIRAL HOOK CAPTIONS" in quick_prompt:
            full_prompt = quick_prompt
        else:
            full_prompt = build_prompt(tool, platform, niche, tone, user_message)

        messages_for_ai = [
            {
                "role": "system",
                "content": """
You are Channel Coach, a helpful AI assistant for creators.
You help with YouTube, TikTok, Shorts, thumbnails, hooks, captions, scripts, hashtags, and content strategy.
You remember the current conversation and can expand, revise, or continue previous ideas.
"""
            }
        ]

        for msg in st.session_state.messages[-10:]:
            messages_for_ai.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        messages_for_ai.append({
            "role": "user",
            "content": full_prompt
        })

        with st.spinner("Channel Coach is creating your content..."):

            if uploaded_file:
                image_bytes = uploaded_file.getvalue()
                image_base64 = base64.b64encode(image_bytes).decode("utf-8")
                mime_type = uploaded_file.type

                image_prompt = full_prompt + """

Also analyze the uploaded image.
Give feedback on:
1. Thumbnail strength
2. Text readability
3. Hook potential
4. Visual appeal
5. Better title ideas
6. Better on-screen text ideas
"""

                response = client.responses.create(
                    model="gpt-4.1-mini",
                    input=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "input_text", "text": image_prompt},
                                {
                                    "type": "input_image",
                                    "image_url": f"data:{mime_type};base64,{image_base64}"
                                }
                            ]
                        }
                    ]
                )

            else:
                response = client.responses.create(
                    model="gpt-4.1-mini",
                    input=messages_for_ai
                )

        reply = response.output_text
        st.session_state.messages.append({"role": "assistant", "content": reply})

st.divider()
st.markdown("### 💬 Results")

for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):

        if message["role"] == "assistant":
            st.markdown("### ✨ Your Results")
            st.caption("📋 Click inside the box, press Ctrl + A, then Ctrl + C to copy.")

            st.text_area(
                "Copyable result",
                message["content"],
                height=300,
                key=f"text_{i}"
            )

        else:
            st.write(message["content"])