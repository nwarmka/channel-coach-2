# Channel Coach - Creator Toolkit UI

import gradio as gr

from features import (
    analyze_thumbnail,
    description_help,
    generate_creator_memory_insights,
    generate_titles,
    render_creator_memory_snapshot,
    render_video_review_history,
    seo_help,
    shorts_ideas,
    video_analyzer_with_history,
)


def build_toolkit_page(workspace_name, visible=False):
    """Build the Creator Toolkit page and wire all toolkit events."""

    with gr.Column(
        visible=visible,
        elem_id="toolkit-page",
    ) as toolkit_page:

        gr.Markdown(
            "## 🎬 Creator Toolkit\n\n"
            "Analyze videos, improve thumbnails, generate titles, "
            "optimize SEO, write descriptions, and brainstorm content ideas."
        )

        # =====================================================
        # VIDEO ANALYZER
        # =====================================================
        with gr.Accordion("🎥 Video Analyzer", open=True):
            gr.Markdown(
                """
                ## 🎥 Video Analyzer
                Upload a long-form video, Short, Reel, TikTok, or
                Facebook Reel and get creator feedback. Channel Coach
                will sample frames and give pacing, hook, thumbnail,
                title, and editing advice.
                """
            )

            analyzer_upload = gr.Video(
                label="Upload Video"
            )

            analyzer_type = gr.Dropdown(
                [
                    "Long-form YouTube Video",
                    "YouTube Short",
                    "TikTok",
                    "Instagram Reel",
                    "Facebook Reel",
                ],
                value="Long-form YouTube Video",
                label="Video Type",
            )

            analyzer_notes = gr.Textbox(
                label="Optional Notes",
                lines=6,
                placeholder=(
                    "Example: This is my Ice Rod guide. Tell me what "
                    "to cut, where to add text, and if the pacing feels good."
                ),
            )

            analyzer_button = gr.Button(
                "🎥 Analyze Video"
            )

            analyzer_output = gr.Textbox(
                label="Video Feedback",
                lines=18,
            )

        # =====================================================
        # REVIEW HISTORY
        # =====================================================
        with gr.Accordion("📚 Review History", open=False):
            review_history_output = gr.HTML(
                value=render_video_review_history("main")
            )

            review_history_refresh = gr.Button(
                "🔄 Refresh Review History"
            )

            review_history_refresh.click(
                render_video_review_history,
                inputs=[workspace_name],
                outputs=review_history_output,
            )

        analyzer_button.click(
            video_analyzer_with_history,
            inputs=[
                analyzer_upload,
                analyzer_notes,
                analyzer_type,
            ],
            outputs=[
                analyzer_output,
                review_history_output,
            ],
            show_progress="full",
        )

        # =====================================================
        # CREATOR MEMORY INSIGHTS
        # =====================================================
        with gr.Accordion(
            "🧠 Creator Memory Insights",
            open=False,
        ):
            gr.Markdown(
                """
                Generate pattern-based insights from your saved video
                reviews. Channel Coach will look for repeated strengths,
                weak spots, score trends, and your next best focus.
                """
            )

            creator_memory_snapshot = gr.HTML(
                value=render_creator_memory_snapshot()
            )

            creator_memory_button = gr.Button(
                "✨ Generate Creator Insights"
            )

            creator_memory_output = gr.Textbox(
                label="Creator Memory Insights",
                lines=16,
            )

            creator_memory_button.click(
                generate_creator_memory_insights,
                inputs=[],
                outputs=creator_memory_output,
                show_progress="full",
            )

        # =====================================================
        # THUMBNAIL REVIEW
        # =====================================================
        with gr.Accordion("🖼 Thumbnail Review", open=False):
            thumbnail_input = gr.Image(
                type="filepath",
                label="Upload Thumbnail",
            )

            thumbnail_button = gr.Button(
                "🖼 Review Thumbnail"
            )

            thumbnail_output = gr.Textbox(
                label="Thumbnail Feedback",
                lines=16,
            )

            thumbnail_button.click(
                analyze_thumbnail,
                inputs=[
                    thumbnail_input,
                    workspace_name,
                ],
                outputs=thumbnail_output,
                show_progress="full",
            )

        # =====================================================
        # TITLE GENERATOR
        # =====================================================
        with gr.Accordion("🏷 Title Generator", open=False):
            title_input = gr.Textbox(
                label="Video Idea",
                lines=4,
            )

            title_platform = gr.Dropdown(
                [
                    "YouTube Shorts",
                    "TikTok",
                    "Instagram Reels",
                    "YouTube Long Form",
                ],
                value="YouTube Shorts",
                label="Platform",
            )

            title_tone = gr.Dropdown(
                [
                    "Bold",
                    "Funny",
                    "Friendly",
                    "Casual",
                    "Professional",
                ],
                value="Bold",
                label="Tone",
            )

            title_button = gr.Button(
                "✨ Generate Titles"
            )

            title_output = gr.Textbox(
                label="Title Ideas",
                lines=12,
            )

            title_button.click(
                generate_titles,
                inputs=[
                    title_input,
                    title_platform,
                    title_tone,
                    workspace_name,
                ],
                outputs=title_output,
                show_progress="full",
            )

        # =====================================================
        # SEO OPTIMIZER
        # =====================================================
        with gr.Accordion("🔍 SEO Optimizer", open=False):
            seo_input = gr.Textbox(
                label="Video Idea",
                lines=4,
            )

            seo_platform = gr.Dropdown(
                [
                    "YouTube Shorts",
                    "TikTok",
                    "Instagram Reels",
                    "YouTube Long Form",
                ],
                value="YouTube Shorts",
                label="Platform",
            )

            seo_niche = gr.Textbox(
                label="Niche",
                value="Gaming creator",
            )

            seo_button = gr.Button(
                "🔍 Generate SEO Plan"
            )

            seo_output = gr.Textbox(
                label="SEO Results",
                lines=14,
            )

            seo_button.click(
                seo_help,
                inputs=[
                    seo_input,
                    seo_platform,
                    seo_niche,
                    workspace_name,
                ],
                outputs=seo_output,
                show_progress="full",
            )

        # =====================================================
        # DESCRIPTION WRITER
        # =====================================================
        with gr.Accordion("📝 Description Writer", open=False):
            desc_input = gr.Textbox(
                label="Video Idea",
                lines=4,
            )

            desc_platform = gr.Dropdown(
                [
                    "YouTube Shorts",
                    "TikTok",
                    "Instagram Reels",
                    "YouTube Long Form",
                ],
                value="YouTube Shorts",
                label="Platform",
            )

            desc_niche = gr.Textbox(
                label="Niche",
                value="Gaming creator",
            )

            desc_button = gr.Button(
                "📝 Write Description"
            )

            desc_output = gr.Textbox(
                label="Description",
                lines=14,
            )

            desc_button.click(
                description_help,
                inputs=[
                    desc_input,
                    desc_platform,
                    desc_niche,
                    workspace_name,
                ],
                outputs=desc_output,
                show_progress="full",
            )

        # =====================================================
        # CONTENT IDEAS
        # =====================================================
        with gr.Accordion("💡 Content Ideas", open=False):
            niche_input = gr.Textbox(
                label="Niche",
                value="Retro gaming",
            )

            topic_input = gr.Textbox(
                label="Game or Topic",
                value="A Link to the Past",
            )

            ideas_button = gr.Button(
                "💡 Generate Ideas"
            )

            ideas_output = gr.Textbox(
                label="Shorts Ideas",
                lines=16,
            )

            ideas_button.click(
                shorts_ideas,
                inputs=[
                    niche_input,
                    topic_input,
                    workspace_name,
                ],
                outputs=ideas_output,
                show_progress="full",
            )

    return toolkit_page

