import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
import streamlit.components.v1 as components

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
.result-box {
    padding: 20px;
    border-radius: 18px;
    background-color: #ffffff;
    border: 1px solid #ddd;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🎬 Channel Coach</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">AI tools for YouTube, TikTok, Shorts, captions, hooks, hashtags, and content growth.</p>', unsafe_allow_html=True)

st.divider()

# Sidebar
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

st.sidebar.caption("Built by Nikki | Channel Coach v1")

# Main layout
left, right = st.columns([1, 1])

with left:
    st.markdown("### ✍️ Describe Your Content")

    user_text = st.text_area(
        "Video idea, script, comment, or content topic",
        placeholder="Example: A Paper Mario boss fight short where Mario barely wins...",
        height=180
    )

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

    st.info("Tip: For best results, include the video topic, audience, goal, and platform.")

if "messages" not in st.session_state:
    st.session_state.messages = []

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

Rules:
- Be specific, not generic.
- Use SEO-rich language when helpful.
- Make it catchy but not cringe.
- Give ready-to-copy examples.
- Focus on hooks, retention, discoverability, and engagement.
"""

if quick_prompt:
    if not quick_prompt.strip():
        st.warning("Please describe your video or type a request first.")
    else:
        st.session_state.messages.append({"role": "user", "content": quick_prompt})

        if "VIRAL HOOK CAPTIONS" in quick_prompt:
            full_prompt = quick_prompt
        else:
            full_prompt = build_prompt(tool, platform, niche, tone, quick_prompt)

        with st.spinner("Channel Coach is creating your content..."):
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=full_prompt
            )

        reply = response.output_text
        st.session_state.messages.append({"role": "assistant", "content": reply})

st.divider()
st.markdown("### 💬 Results")

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
                height=250,
                key=f"text_{i}"
            )

        else:
            st.write(message["content"])