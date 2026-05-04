import streamlit as st
from openai import OpenAI
import base64

# -----------------------------
# PAGE SETUP
# -----------------------------
st.set_page_config(
    page_title="Channel Coach",
    page_icon="🎬",
    layout="wide"
)

# -----------------------------
# OPENAI CLIENT
# -----------------------------
api_key = st.secrets.get("OPENAI_API_KEY", None)

if not api_key:
    st.error("OPENAI_API_KEY is missing. Add it in Streamlit Cloud → Manage app → Settings → Secrets.")
    st.stop()

client = OpenAI(api_key=api_key)

# -----------------------------
# STYLES
# -----------------------------
st.markdown(
    """
    <style>
    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .subtitle {
        font-size: 18px;
        color: #666;
        margin-bottom: 25px;
    }
    .section-card {
        padding: 18px;
        border-radius: 16px;
        background-color: #f7f7f9;
        border: 1px solid #e5e5e5;
        margin-bottom: 16px;
    }
    .small-note {
        font-size: 14px;
        color: #777;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def image_to_base64(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode("utf-8")


def ask_text_ai(prompt):
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )
    return response.output_text


def ask_image_ai(prompt, uploaded_image):
    image_base64 = image_to_base64(uploaded_image)
    mime_type = uploaded_image.type or "image/png"

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": f"data:{mime_type};base64,{image_base64}"
                    }
                ]
            }
        ]
    )
    return response.output_text


# -----------------------------
# HEADER
# -----------------------------
st.markdown('<div class="main-title">🎬 Channel Coach</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">A creator assistant for better titles, hooks, captions, thumbnails, and video ideas.</div>',
    unsafe_allow_html=True
)

# -----------------------------
# SIDEBAR CREATOR PROFILE
# -----------------------------
st.sidebar.header("Creator Profile")

creator_name = st.sidebar.text_input("Creator or channel name", placeholder="Example: Nikki Plays")
platform = st.sidebar.selectbox(
    "Main platform",
    [
        "YouTube",
        "TikTok",
        "Instagram Reels",
        "Facebook Reels",
        "YouTube + TikTok",
        "Multiple platforms"
    ]
)

niche = st.sidebar.selectbox(
    "Creator niche",
    [
        "Gaming",
        "Lifestyle",
        "Beauty",
        "Fitness",
        "Food/Cooking",
        "Travel",
        "Family/Vlogs",
        "Deportee wife / life in Mexico",
        "Education/Tutorials",
        "Comedy",
        "Music",
        "Business",
        "Other"
    ]
)

custom_niche = ""
if niche == "Other":
    custom_niche = st.sidebar.text_input("Type your niche")

tone = st.sidebar.selectbox(
    "Content tone",
    [
        "Friendly",
        "Funny",
        "Helpful",
        "Dramatic",
        "Cozy",
        "High-energy",
        "Professional",
        "Emotional/storytelling"
    ]
)

audience = st.sidebar.text_area(
    "Who is your audience?",
    placeholder="Example: Nintendo fans, moms, people moving to Mexico, beginners, etc."
)

creator_profile = f"""
Creator/channel name: {creator_name or 'Not provided'}
Main platform: {platform}
Niche: {custom_niche if niche == 'Other' else niche}
Tone: {tone}
Audience: {audience or 'Not provided'}
"""

# -----------------------------
# MAIN TABS
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🚀 Quick Tools",
    "🖼️ Thumbnail Review",
    "🎥 Video Upload Coach",
    "💡 Idea Builder"
])

# -----------------------------
# TAB 1: QUICK TOOLS
# -----------------------------
with tab1:
    st.header("🚀 Quick Creator Tools")
    st.write("Use these tools for fast titles, captions, hashtags, hooks, and post ideas.")

    content_description = st.text_area(
        "Describe your video or short",
        placeholder="Example: Flurrie blows the Punies across the gap in Paper Mario TTYD. The on-screen text says teamwork wins again."
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Generate Better Titles"):
            if not content_description:
                st.warning("Describe your video first.")
            else:
                prompt = f"""
You are Channel Coach, a creator growth assistant.

Creator profile:
{creator_profile}

Video description:
{content_description}

Create 12 strong title options.
Separate them into:
1. Search-friendly titles
2. Curiosity/clickable titles
3. Shorts/Reels/TikTok titles

Make them specific, not generic.
Avoid clickbait that lies.
"""
                with st.spinner("Creating title ideas..."):
                    st.write(ask_text_ai(prompt))

        if st.button("Generate SEO Captions + Hashtags"):
            if not content_description:
                st.warning("Describe your video first.")
            else:
                prompt = f"""
You are Channel Coach, a creator growth assistant.

Creator profile:
{creator_profile}

Video description:
{content_description}

Create:
1. A YouTube description with SEO-rich language
2. A TikTok caption
3. A Facebook Reels caption
4. 15 hashtags, each under 20 characters when possible
5. 10 keyword phrases the creator could naturally use

Make it useful, specific, and platform-friendly.
"""
                with st.spinner("Creating SEO captions..."):
                    st.write(ask_text_ai(prompt))

    with col2:
        if st.button("Generate Hook Ideas"):
            if not content_description:
                st.warning("Describe your video first.")
            else:
                prompt = f"""
You are Channel Coach, a creator growth assistant.

Creator profile:
{creator_profile}

Video description:
{content_description}

Create:
1. 10 opening hook lines
2. 10 on-screen text hook ideas
3. 5 voiceover hook ideas
4. Explain which 3 are strongest and why

Keep hooks short, clear, and attention-grabbing.
"""
                with st.spinner("Creating hooks..."):
                    st.write(ask_text_ai(prompt))

        if st.button("Improve My Post"):
            if not content_description:
                st.warning("Paste your post or description first.")
            else:
                prompt = f"""
You are Channel Coach, a creator growth assistant.

Creator profile:
{creator_profile}

User's current post/video idea:
{content_description}

Improve this for social media.
Give:
1. What is working
2. What is confusing
3. A stronger version
4. Better caption
5. Better title
6. Better hashtags
7. Better on-screen text
"""
                with st.spinner("Improving your post..."):
                    st.write(ask_text_ai(prompt))

# -----------------------------
# TAB 2: THUMBNAIL REVIEW
# -----------------------------
with tab2:
    st.header("🖼️ Thumbnail Review")
    st.write("Upload a thumbnail or screenshot and Channel Coach will critique it before you post.")

    uploaded_thumbnail = st.file_uploader(
        "Upload thumbnail or screenshot",
        type=["png", "jpg", "jpeg"],
        key="thumbnail_upload"
    )

    thumbnail_context = st.text_area(
        "What is this video about?",
        placeholder="Example: This is a Paper Mario short where Flurrie pushes Punies across a gap.",
        key="thumbnail_context"
    )

    if uploaded_thumbnail:
        st.image(uploaded_thumbnail, caption="Uploaded thumbnail/screenshot", use_container_width=True)

    if st.button("Analyze Thumbnail"):
        if not uploaded_thumbnail:
            st.warning("Upload an image first.")
        else:
            prompt = f"""
You are Channel Coach, a creator thumbnail and video growth expert.

Creator profile:
{creator_profile}

Video context:
{thumbnail_context or 'No extra context provided.'}

Analyze the uploaded thumbnail/screenshot.
Give feedback on:
1. Thumbnail strength from 1-10
2. Text readability
3. Hook potential
4. Visual appeal
5. Whether it would stop someone from scrolling
6. What is confusing
7. What should be bigger, brighter, or removed
8. Better title ideas
9. Better on-screen text ideas
10. A simple redesign plan the creator can follow in Canva

Be honest but encouraging.
Give specific changes, not generic advice.
"""
            with st.spinner("Analyzing thumbnail..."):
                st.write(ask_image_ai(prompt, uploaded_thumbnail))

# -----------------------------
# TAB 3: VIDEO UPLOAD COACH
# -----------------------------
with tab3:
    st.header("🎥 Video Upload Coach")
    st.write("Upload a short video file or describe the video. For now, Channel Coach can coach based on your description and file details.")

    uploaded_video = st.file_uploader(
        "Upload video file",
        type=["mp4", "mov", "m4v", "webm"],
        key="video_upload"
    )

    video_description = st.text_area(
        "Describe what happens in the video",
        placeholder="Example: Mario and Flurrie help the Punies cross the gap. The clip is about teamwork and puzzle solving.",
        key="video_description"
    )

    current_title = st.text_input("Current title, if you have one", key="current_title")
    current_caption = st.text_area("Current caption/description, if you have one", key="current_caption")

    if uploaded_video:
        st.video(uploaded_video)
        st.info(f"Uploaded file: {uploaded_video.name}")

    if st.button("Coach My Video"):
        if not video_description and not uploaded_video:
            st.warning("Upload a video or describe it first.")
        else:
            file_note = ""
            if uploaded_video:
                file_note = f"The user uploaded a video file named {uploaded_video.name}. You cannot directly watch the full video here, so coach based on the user's description and file context."

            prompt = f"""
You are Channel Coach, a creator growth assistant.

Creator profile:
{creator_profile}

{file_note}

Video description:
{video_description or 'No detailed description provided.'}

Current title:
{current_title or 'Not provided'}

Current caption:
{current_caption or 'Not provided'}

Give a complete pre-posting review:
1. Stronger title options
2. Stronger hook ideas
3. Better first 3 seconds idea
4. SEO-rich YouTube description
5. TikTok caption
6. Facebook Reels caption
7. Hashtags
8. On-screen text ideas
9. Editing suggestions
10. Thumbnail idea
11. What might confuse viewers
12. Final post checklist

Be specific to the creator's niche and video.
"""
            with st.spinner("Coaching your video..."):
                st.write(ask_text_ai(prompt))

# -----------------------------
# TAB 4: IDEA BUILDER
# -----------------------------
with tab4:
    st.header("💡 Idea Builder")
    st.write("Build unique video ideas for your niche.")

    goal = st.selectbox(
        "What do you want?",
        [
            "More views",
            "More subscribers/followers",
            "More comments",
            "Better SEO/search traffic",
            "More relatable content",
            "A unique series idea",
            "Short-form ideas",
            "Long-form video ideas"
        ]
    )

    idea_notes = st.text_area(
        "Tell Channel Coach what you want help with",
        placeholder="Example: I need shorts ideas for Paper Mario that feel like helpful mini-guides."
    )

    if st.button("Build Ideas"):
        prompt = f"""
You are Channel Coach, a creator growth assistant.

Creator profile:
{creator_profile}

Goal:
{goal}

User notes:
{idea_notes or 'No extra notes provided.'}

Create:
1. 15 video ideas
2. 10 short-form ideas
3. 5 series ideas
4. 5 ideas that feel unique and less generic
5. Best idea to post first and why
6. Simple filming/editing checklist

Make the ideas specific to the creator's niche.
"""
        with st.spinner("Building ideas..."):
            st.write(ask_text_ai(prompt))

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.markdown(
    "<p class='small-note'>Channel Coach helps creators brainstorm and improve content before posting. Always review results before publishing.</p>",
    unsafe_allow_html=True
)
