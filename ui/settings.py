# Channel Coach - Settings UI

import gradio as gr

from features import (
    load_creator_profile,
    render_getting_started_checklist,
    save_creator_profile_and_refresh_dashboard,
)


def build_settings_page(
    workspace_name,
    dashboard_output,
    visible=False,
):
    """
    Build Settings, Getting Started, and Creator Profile.

    Returns the page plus the components app.py needs when a workspace loads.
    """

    saved_profile = load_creator_profile("main")

    with gr.Column(
        visible=visible,
        elem_id="settings-page",
    ) as settings_page:

        gr.Markdown(
            "## ⚙️ Settings\n\n"
            "Manage your creator profile and app preferences."
        )

        with gr.Accordion("🚀 Getting Started", open=True):
            onboarding_output = gr.HTML(
                value=render_getting_started_checklist("main")
            )

            onboarding_refresh_button = gr.Button(
                "🔄 Refresh Getting Started"
            )

            onboarding_refresh_button.click(
                render_getting_started_checklist,
                inputs=[workspace_name],
                outputs=onboarding_output,
            )

        with gr.Accordion("👤 Creator Profile", open=True):
            gr.Markdown(
                """
                ## 👤 Creator Profile & Preferences
                Save your channel niche, goals, style, and current
                content here. Channel Coach will use this information
                in every tool.
                """
            )

            profile_channel_name = gr.Textbox(
                label="Channel Name",
                value=saved_profile.get("channel_name", ""),
                placeholder="Example: My Awesome Gaming Channel",
            )

            profile_creator_name = gr.Textbox(
                label="Creator Name",
                value=saved_profile.get("creator_name", ""),
                placeholder="Example: Nicole, Alex, Gamer Mom, etc.",
            )

            profile_niche = gr.Textbox(
                label="Niche",
                value=saved_profile.get("niche", ""),
                placeholder=(
                    "Example: Retro gaming, cooking, travel, "
                    "tech reviews..."
                ),
                lines=3,
            )

            profile_target_audience = gr.Textbox(
                label="Target Audience",
                value=saved_profile.get("target_audience", ""),
                placeholder=(
                    "Example: Beginners, cozy gamers, busy parents, "
                    "tech newbies..."
                ),
                lines=3,
            )

            profile_content_style = gr.Textbox(
                label="Content Style",
                value=saved_profile.get("content_style", ""),
                placeholder=(
                    "Example: Funny, helpful, cozy, direct, "
                    "chaotic-good, cinematic..."
                ),
                lines=3,
            )

            profile_current_games = gr.Textbox(
                label="Current Games / Current Content",
                value=saved_profile.get("current_games", ""),
                placeholder=(
                    "Example: Stardew Valley guides, Zelda walkthroughs, "
                    "budget recipes..."
                ),
                lines=3,
            )

            profile_main_platforms = gr.Textbox(
                label="Main Platforms",
                value=saved_profile.get("main_platforms", ""),
                placeholder=(
                    "Example: YouTube, TikTok, Instagram Reels, "
                    "Facebook Reels"
                ),
            )

            profile_goals = gr.Textbox(
                label="Goals",
                value=saved_profile.get("goals", ""),
                placeholder=(
                    "Example: Grow subscribers, improve thumbnails, "
                    "post 3 Shorts a week..."
                ),
                lines=3,
            )

            profile_preferred_tone = gr.Textbox(
                label="Preferred Coaching Tone",
                value=saved_profile.get("preferred_tone", ""),
                placeholder=(
                    "Example: Friendly, honest, motivating, "
                    "not too corporate..."
                ),
                lines=3,
            )

            profile_things_to_avoid = gr.Textbox(
                label="Things Channel Coach Should Avoid",
                value=saved_profile.get("things_to_avoid", ""),
                placeholder=(
                    "Example: Fake clickbait, generic advice, "
                    "too much jargon..."
                ),
                lines=3,
            )

            profile_save_button = gr.Button(
                "💾 Save Creator Profile"
            )

            profile_save_status = gr.Textbox(
                label="Save Status",
                lines=2,
            )

            profile_save_button.click(
                save_creator_profile_and_refresh_dashboard,
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
                    profile_things_to_avoid,
                    workspace_name,
                ],
                outputs=[
                    profile_save_status,
                    dashboard_output,
                    onboarding_output,
                ],
            )

    return {
        "page": settings_page,
        "onboarding_output": onboarding_output,
        "profile_channel_name": profile_channel_name,
        "profile_creator_name": profile_creator_name,
        "profile_niche": profile_niche,
        "profile_target_audience": profile_target_audience,
        "profile_content_style": profile_content_style,
        "profile_current_games": profile_current_games,
        "profile_main_platforms": profile_main_platforms,
        "profile_goals": profile_goals,
        "profile_preferred_tone": profile_preferred_tone,
        "profile_things_to_avoid": profile_things_to_avoid,
    }

