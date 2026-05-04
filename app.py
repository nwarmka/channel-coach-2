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
    .helper-box {
        padding: 16px;
        border-radius: 14px;
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


def build_creator_profile(creator_name, platform, niche, custom_niche, tone, audience):
    selected_niche = custom_niche if niche == "Other" else niche
    return f"""
Creator/channel name: {creator_name or 'Not provided'}
Main platform: {platform}
Selected niche: {selected_niche}
Tone: {tone}
Audience: {audience or 'Not provided'}
"""

# -----------------------------
# HEADER
# -----------------------------
st.markdown('<div class="main-title">🎬 Channel Coach</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">A creator assistant for better titles, hooks, captions, thumbnails, videos, and growth ideas.</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="helper-box">
    <b>How to use this:</b><br>
    1. Fill out the Creator Profile on the left.<br>
    2. Pick a tab depending on what you need.<br>
    3. Paste your video idea, upload a short clip, upload a thumbnail, or paste a YouTube link.<br>
    4. Let Channel Coach improve your content before you post.
    </div>
    """,
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
        "Auto-detect from my idea",
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

creator_profile = build_creator_profile(creator_name, platform, niche, custom_niche, tone, audience)

# -----------------------------
# MAIN TABS
# -----------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🚀 Quick Tools",
    "🖼️ Thumbnail Review",
    "🎥 Video Upload Coach",
    "🔗 YouTube Link Coach",
    "🛠️ Fix My Video",
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

If the niche says auto-detect, identify the most likely niche first.

Create 12 strong title options.
Separate them into:
1. Search-friendly titles
2. Curiosity/clickable titles
3. Shorts/Reels/TikTok titles

Make them specific, not generic.
Avoid fake clickbait.
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

If the niche says auto-detect, identify the most likely niche first.

Create:
1. A YouTube description with SEO-rich language
2. A TikTok caption
3. An Instagram Reels caption
4. A Facebook Reels caption
5. 15 hashtags, each under 20 characters when possible
6. 10 keyword phrases the creator could naturally use

Make it specific, searchable, and not generic.
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

If the niche says auto-detect, identify the most likely niche first.

Create:
1. 10 opening hook lines
2. 10 on-screen text hook ideas
3. 5 voiceover hook ideas
4. A stronger first 3 seconds plan
5. Explain which 3 hooks are strongest and why

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

If the niche says auto-detect, identify the most likely niche first.

Improve this for social media.
Give:
1. What is working
2. What is confusing
3. A stronger version
4. Better caption
5. Better title
6. Better hashtags
7. Better on-screen text
8. What to change before posting
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

If the niche says auto-detect, identify the most likely niche first.

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
    st.write("Upload a short video clip. Shorts usually work best because long videos may be too large for Streamlit.")

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

    if st.button("Coach My Uploaded Video"):
        if not video_description and not uploaded_video:
            st.warning("Upload a video or describe it first.")
        else:
            file_note = ""
            if uploaded_video:
                file_note = f"The user uploaded a video file named {uploaded_video.name}. You cannot directly watch every frame here, so coach based on the user's description, title, caption, and file context."

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

If the niche says auto-detect, identify the most likely niche first.

Give a complete pre-posting review:
1. Detected niche
2. Stronger title options
3. Stronger hook ideas
4. Better first 3 seconds idea
5. SEO-rich YouTube description
6. TikTok caption
7. Instagram Reels caption
8. Facebook Reels caption
9. Hashtags
10. On-screen text ideas
11. Editing suggestions
12. Thumbnail idea
13. What might confuse viewers
14. Final post checklist

Be specific to the creator's niche and video.
"""
            with st.spinner("Coaching your uploaded video..."):
                st.write(ask_text_ai(prompt))

# -----------------------------
# TAB 4: YOUTUBE LINK COACH
# -----------------------------
with tab4:
    st.header("🔗 YouTube Link Coach")
    st.write("Paste a YouTube link and describe what happens in the video. This is useful when the file is too big to upload.")

    youtube_link = st.text_input("Paste YouTube link", placeholder="https://www.youtube.com/watch?v=...")
    link_context = st.text_area(
        "Describe the video or paste your current title/description",
        placeholder="Example: This is my long-form Paper Mario episode where I get Flurrie and help the Punies. I want better SEO and a better title."
    )

    if st.button("Analyze YouTube Link"):
        if not youtube_link and not link_context:
            st.warning("Paste a YouTube link or describe the video first.")
        else:
            prompt = f"""
You are Channel Coach, a creator growth assistant.

Creator profile:
{creator_profile}

YouTube link:
{youtube_link or 'No link provided'}

Video context/current description:
{link_context or 'No context provided'}

Important: You cannot directly open the YouTube link from inside this app. Use the link as context only, and coach based on the user's description.

If the niche says auto-detect, identify the most likely niche first.

Give:
1. Detected niche
2. Better YouTube title options
3. Better searchable description
4. Better first paragraph for the description
5. Chapters/timestamps template if this is long-form
6. Better pinned comment idea
7. Better thumbnail concept
8. Better Shorts ideas from this long video
9. SEO keyword phrases
10. Hashtags
11. What to improve before posting or reposting

Make this practical and specific.
"""
            with st.spinner("Analyzing YouTube link context..."):
                st.write(ask_text_ai(prompt))

# -----------------------------
# TAB 5: FIX MY VIDEO
# -----------------------------
with tab5:
    st.header("🛠️ Fix My Video Mode")
    st.write("Paste what you already have, and Channel Coach will rewrite it stronger.")

    fix_platform = st.selectbox(
        "Where are you posting?",
        ["YouTube Long Video", "YouTube Short", "TikTok", "Instagram Reel", "Facebook Reel", "Multiple platforms"]
    )

    bad_title = st.text_input("Current title")
    bad_caption = st.text_area("Current caption or description")
    bad_hashtags = st.text_area("Current hashtags")
    what_happens = st.text_area(
        "What happens in the video?",
        placeholder="Example: Flurrie blows the Punies across a gap and everyone makes it safely across."
    )

    if st.button("Fix My Video"):
        if not what_happens and not bad_title and not bad_caption:
            st.warning("Paste at least a title, caption, or video description first.")
        else:
            prompt = f"""
You are Channel Coach, a creator growth assistant.

Creator profile:
{creator_profile}

Posting platform:
{fix_platform}

Current title:
{bad_title or 'Not provided'}

Current caption/description:
{bad_caption or 'Not provided'}

Current hashtags:
{bad_hashtags or 'Not provided'}

What happens in the video:
{what_happens or 'Not provided'}

If the niche says auto-detect, identify the most likely niche first.

Rewrite and fix everything.
Give:
1. What is weak or confusing
2. Stronger title
3. 10 alternate titles
4. Stronger caption/description
5. Better hashtags
6. Better first 3 seconds hook
7. Better on-screen text
8. Better thumbnail text
9. One simple thing to change before posting
10. Final ready-to-copy version

Make it specific and ready to post.
"""
            with st.spinner("Fixing your video..."):
                st.write(ask_text_ai(prompt))

# -----------------------------
# TAB 6: IDEA BUILDER
# -----------------------------
with tab6:
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

If the niche says auto-detect, identify the most likely niche first.

Create:
1. Detected niche
2. 15 video ideas
3. 10 short-form ideas
4. 5 long-form ideas
5. 5 series ideas
6. 5 ideas that feel unique and less generic
7. Best idea to post first and why
8. Simple filming/editing checklist
9. What makes these ideas different from generic AI suggestions

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
