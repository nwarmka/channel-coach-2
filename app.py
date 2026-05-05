import os
import cv2
import base64
import tempfile
import streamlit as st
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
from openai import OpenAI

# -----------------------------
# SETUP
# -----------------------------
load_dotenv()

st.set_page_config(
    page_title="Channel Coach",
    page_icon="🎬",
    layout="centered"
)

api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

if not api_key:
    st.error("Missing OpenAI API key. Add OPENAI_API_KEY in Streamlit secrets.")
    st.stop()

client = OpenAI(api_key=api_key)
MODEL = "gpt-4.1-mini"

# -----------------------------
# STYLE
# -----------------------------
st.markdown("""
<style>
.big-title {
    font-size: 38px;
    font-weight: 800;
    text-align: center;
}
.subtitle {
    font-size: 18px;
    text-align: center;
    color: #888;
}
.result-box {
    padding: 18px;
    border-radius: 18px;
    background-color: #1f1f2e;
    border: 1px solid #444;
    margin-top: 15px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def ask_channel_coach(prompt):
    response = client.responses.create(
        model=MODEL,
        input=prompt
    )
    return response.output_text


def frame_to_base64(frame):
    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=80)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def extract_video_frames(video_file, max_frames=8):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    temp_file.write(video_file.read())
    temp_file.close()

    video = cv2.VideoCapture(temp_file.name)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    if total_frames <= 0:
        return []

    frame_positions = [
        int(total_frames * i / max_frames)
        for i in range(max_frames)
    ]

    frames = []

    for pos in frame_positions:
        video.set(cv2.CAP_PROP_POS_FRAMES, pos)
        success, frame = video.read()
        if success:
            frames.append(frame_to_base64(frame))

    video.release()
    return frames


def image_to_base64(uploaded_image):
    image = Image.open(uploaded_image).convert("RGB")
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=85)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


# -----------------------------
# HEADER
# -----------------------------
st.markdown('<div class="big-title">🎬 Channel Coach</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">A creator assistant for Shorts, captions, titles, thumbnails, and content ideas.</div>',
    unsafe_allow_html=True
)

st.divider()

# -----------------------------
# CREATOR PROFILE
# -----------------------------
with st.expander("👤 Creator Profile - fill this out first for better results", expanded=True):
    niche = st.selectbox(
        "What kind of creator are you?",
        [
            "Gaming",
            "Lifestyle",
            "Travel",
            "Food",
            "Beauty",
            "Fitness",
            "Deportee / Life in Mexico",
            "Education",
            "Business",
            "Other"
        ]
    )

    platform = st.selectbox(
        "Main platform",
        ["YouTube Shorts", "TikTok", "Instagram Reels", "Facebook Reels", "YouTube Long Form"]
    )

    tone = st.selectbox(
        "Content style",
        [
            "Funny",
            "Helpful",
            "Emotional",
            "Dramatic",
            "Cozy",
            "Educational",
            "High-energy",
            "Beginner-friendly"
        ]
    )

    audience = st.text_input(
        "Who is your audience?",
        placeholder="Example: Nintendo fans, beginner creators, wives of deportees, food lovers"
    )

profile_text = f"""
Creator profile:
- Niche: {niche}
- Platform: {platform}
- Tone: {tone}
- Audience: {audience if audience else "General audience"}
"""

# -----------------------------
# TABS
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🎬 Shorts Analyst",
    "🏷️ Titles & Hashtags",
    "🖼️ Thumbnail Help",
    "💡 Video Ideas"
])

# -----------------------------
# TAB 1: SHORTS ANALYST
# -----------------------------
with tab1:
    st.subheader("🎬 Shorts Analyst")
    st.write("Upload a Short, TikTok, or Reel and get feedback before posting.")
    st.caption("You'll get: hook score, title ideas, fixes, hashtags, and a final posting recommendation.")

    uploaded_short = st.file_uploader(
        "Upload your short video",
        type=["mp4", "mov", "webm"],
        key="short_video"
    )

    if uploaded_short:
        st.video(uploaded_short)

    use_idea_only = st.checkbox("I don't have a video yet — analyze my idea instead")

    short_topic = st.text_area(
        "Describe your Short: what happens, and what moment should people care about?",
        placeholder="Example: Flurrie blows the Punies across a gap to save them.",
        height=100
    )

    with st.expander("👀 See example result"):
        st.markdown("""
🔥 **HOOK SCORE: 6/10**  
The idea is cute, but the first 2 seconds need stronger action.

🎯 **FIX:**  
Start with urgency: “Can Flurrie save them before they fall?”

📈 **BETTER TITLE:**  
“Flurrie Saves the Punies in a CRAZY Escape!”

💬 **FINAL VERDICT:**  
Needs small edits before posting.
""")

    goal = st.selectbox(
        "What do you want this Short to do?",
        [
            "Get more views",
            "Get more comments",
            "Make people laugh",
            "Teach something",
            "Build my channel",
            "Promote a service or product"
        ]
    )

    if st.button("🚀 Analyze & Improve My Short", type="primary"):
        if not uploaded_short and not use_idea_only:
            st.warning("Upload a video or check the idea-only box.")
        elif not short_topic:
            st.warning("Describe your Short first.")
        else:
            with st.spinner("Watching your Short like a viral content expert..."):
                if uploaded_short and not use_idea_only:
                    frames = extract_video_frames(uploaded_short, max_frames=8)

                    if not frames:
                        st.error("I could not read the video. Try uploading a shorter MP4 file.")
                    else:
                        content = [
                            {
                                "type": "input_text",
                                "text": f"""
You are Channel Coach, a short-form video expert.

{profile_text}

Analyze this uploaded short-form video.

Video description:
{short_topic}

Goal:
{goal}

Give feedback in this exact format:

🔥 HOOK SCORE: /10
Explain if the first 1-3 seconds are strong or weak.

👀 VISUAL CLARITY:
Is it obvious what is happening?

📝 ON-SCREEN TEXT:
Give better text for the first 3 seconds.

⚡ PACING:
Does the video feel slow, confusing, or engaging?

🎯 WHAT TO FIX BEFORE POSTING:
Give 3 specific fixes.

📈 BETTER TITLES:
Give 5 title options.

🏷️ HASHTAGS:
Give hashtags for {platform}.

💬 FINAL VERDICT:
Say one of these:
- Ready to post
- Needs small edits
- Needs major changes

Be honest but encouraging.
"""
                            }
                        ]

                        for frame in frames:
                            content.append({
                                "type": "input_image",
                                "image_url": f"data:image/jpeg;base64,{frame}",
                                "detail": "auto"
                            })

                        response = client.responses.create(
                            model=MODEL,
                            input=[
                                {
                                    "role": "user",
                                    "content": content
                                }
                            ]
                        )

                        st.success("Analysis complete!")
                        st.subheader("📊 Your Results")
                        st.markdown(response.output_text)

                else:
                    prompt = f"""
You are Channel Coach, a short-form video expert.

{profile_text}

The creator does not have a video uploaded yet. Analyze the idea instead.

Short idea:
{short_topic}

Goal:
{goal}

Give feedback in this exact format:

🔥 IDEA HOOK SCORE: /10
Is this idea strong enough for short-form content?

🪝 BEST OPENING HOOK:
Give the best first 3 seconds.

📝 ON-SCREEN TEXT:
Give text for the opening.

⚡ PACING PLAN:
Break the short into beginning, middle, and ending.

🎯 WHAT TO FIX BEFORE RECORDING:
Give 3 specific improvements.

📈 BETTER TITLES:
Give 5 title options.

🏷️ HASHTAGS:
Give hashtags for {platform}.

💬 FINAL VERDICT:
Say if this idea is ready to record, needs small changes, or needs a stronger concept.
"""
                    result = ask_channel_coach(prompt)

                    st.success("Idea analysis complete!")
                    st.subheader("📊 Your Results")
                    st.markdown(result)

# -----------------------------
# TAB 2: TITLES & HASHTAGS
# -----------------------------
with tab2:
    st.subheader("🏷️ Titles, Captions & Hashtags")
    st.write("Use this when you already know what your video is about.")

    video_description = st.text_area(
        "Describe your video",
        placeholder="Example: Mario rescues the trapped Punies after they get captured.",
        height=120
    )

    content_type = st.selectbox(
        "What do you need?",
        [
            "Everything",
            "Titles only",
            "SEO caption only",
            "Hashtags only",
            "On-screen text ideas"
        ]
    )

    if st.button("Create Titles / Captions / Hashtags"):
        if not video_description:
            st.warning("Describe your video first.")
        else:
            with st.spinner("Creating creator-friendly results..."):
                prompt = f"""
You are Channel Coach.

{profile_text}

Video description:
{video_description}

The creator needs:
{content_type}

Create results in this format:

🔥 BEST TITLE:
Give the strongest title.

📈 WHY IT WORKS:
Explain simply.

🎯 MORE TITLE OPTIONS:
Give 7 options.

📝 SEO CAPTION:
Write a strong caption using searchable language.

💬 ON-SCREEN TEXT:
Give 5 short text overlay ideas.

🏷️ HASHTAGS:
Give hashtags for {platform}.

Make it useful, specific, and not generic.
"""
                result = ask_channel_coach(prompt)
                st.subheader("📊 Your Results")
                st.markdown(result)

# -----------------------------
# TAB 3: THUMBNAIL HELP
# -----------------------------
with tab3:
    st.subheader("🖼️ Thumbnail Help")
    st.write("Upload a thumbnail or screenshot and get feedback.")

    uploaded_image = st.file_uploader(
        "Upload thumbnail or screenshot",
        type=["png", "jpg", "jpeg"],
        key="thumbnail"
    )

    thumbnail_context = st.text_area(
        "What is the video about?",
        placeholder="Example: Mario enters the Great Tree and finds the trapped Punies.",
        height=90
    )

    if uploaded_image:
        st.image(uploaded_image, caption="Uploaded image", use_container_width=True)

    if st.button("Analyze Thumbnail"):
        if not uploaded_image:
            st.warning("Upload a thumbnail or screenshot first.")
        elif not thumbnail_context:
            st.warning("Tell me what the video is about.")
        else:
            with st.spinner("Analyzing thumbnail like a viewer scrolling fast..."):
                image_b64 = image_to_base64(uploaded_image)

                response = client.responses.create(
                    model=MODEL,
                    input=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "input_text",
                                    "text": f"""
You are Channel Coach.

{profile_text}

Analyze this thumbnail or screenshot.

Video context:
{thumbnail_context}

Give feedback in this exact format:

🖼️ THUMBNAIL SCORE: /10

👀 FIRST IMPRESSION:
Would someone understand it quickly?

📝 TEXT READABILITY:
Is the text easy to read? If there is no text, suggest text.

🎯 CLICKABILITY:
Would this make someone click?

🔧 WHAT TO FIX:
Give 3 specific improvements.

🔥 BETTER THUMBNAIL TEXT:
Give 5 short options.

📈 TITLE PAIRINGS:
Give 5 title ideas that match the thumbnail.
"""
                                },
                                {
                                    "type": "input_image",
                                    "image_url": f"data:image/jpeg;base64,{image_b64}",
                                    "detail": "auto"
                                }
                            ]
                        }
                    ]
                )

                st.subheader("📊 Your Results")
                st.markdown(response.output_text)

# -----------------------------
# TAB 4: VIDEO IDEAS
# -----------------------------
with tab4:
    st.subheader("💡 Video Ideas & Scripts")
    st.write("Use this when you need ideas, structure, or a simple script.")

    idea_topic = st.text_area(
        "What do you want to make content about?",
        placeholder="Example: A Link to the Past first episode guide, Paper Mario Punies escaping, life in Mexico content",
        height=120
    )

    idea_type = st.selectbox(
        "What do you want?",
        [
            "Shorts ideas",
            "Long-form video outline",
            "Step-by-step guide script",
            "Hook ideas",
            "Content plan"
        ]
    )

    if st.button("Generate Ideas"):
        if not idea_topic:
            st.warning("Tell me your topic first.")
        else:
            with st.spinner("Building ideas for your channel..."):
                prompt = f"""
You are Channel Coach.

{profile_text}

Topic:
{idea_topic}

Request:
{idea_type}

Give the creator practical, specific ideas.

Format:

🔥 BEST IDEA:
Give the strongest idea first.

🎬 VIDEO STRUCTURE:
Break it into simple parts.

🪝 HOOK OPTIONS:
Give 5 hooks.

📝 SCRIPT / TALKING POINTS:
Give beginner-friendly talking points.

📈 WHY THIS COULD WORK:
Explain why it could get attention.

🏷️ TITLE + HASHTAGS:
Give title options and hashtags.
"""
                result = ask_channel_coach(prompt)
                st.subheader("📊 Your Results")
                st.markdown(result)

# -----------------------------
# FOOTER
# -----------------------------
st.divider()
st.caption("Channel Coach helps creators improve Shorts, captions, thumbnails, titles, and content ideas before posting.")