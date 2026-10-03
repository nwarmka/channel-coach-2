# Channel Coach - Settings UI

import gradio as gr

from features import (
    load_creator_profile,
    render_getting_started_checklist,
    save_creator_profile_and_refresh_dashboard,
)


ENABLE_PUSH_JS = r"""
async (workspace) => {
    try {
        if (!("serviceWorker" in navigator) || !("PushManager" in window)) {
            return "❌ Push notifications are not supported on this device/browser.";
        }

        if (!workspace) {
            return "❌ Log in before enabling reminders.";
        }

        const permission = await Notification.requestPermission();

        if (permission !== "granted") {
            return "Notifications were not allowed. You can enable them later in your browser/app settings.";
        }

        const registration = await navigator.serviceWorker.ready;

        const keyResponse = await fetch("/api/push/vapid-public-key");
        const keyData = await keyResponse.json();

        if (!keyResponse.ok || !keyData.public_key) {
            return "❌ Push reminders are not configured on the server yet.";
        }

        function urlBase64ToUint8Array(base64String) {
            const padding = "=".repeat((4 - base64String.length % 4) % 4);
            const base64 = (base64String + padding)
                .replace(/-/g, "+")
                .replace(/_/g, "/");

            const rawData = window.atob(base64);
            return Uint8Array.from([...rawData].map((char) => char.charCodeAt(0)));
        }

        let subscription = await registration.pushManager.getSubscription();

        if (!subscription) {
            subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: urlBase64ToUint8Array(keyData.public_key),
            });
        }

        const response = await fetch("/api/push/subscribe", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                workspace: workspace,
                subscription: subscription.toJSON(),
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC"
            })
        });

        const result = await response.json();

        if (!response.ok || !result.ok) {
            return "❌ " + (result.message || "Could not enable reminders.");
        }

        return "✅ Content reminders are enabled on this device.";
    } catch (error) {
        console.error("Enable push reminders failed:", error);
        return "❌ Could not enable content reminders.";
    }
}
"""


DISABLE_PUSH_JS = r"""
async (workspace) => {
    try {
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.getSubscription();

        if (!subscription) {
            return "Content reminders are already disabled on this device.";
        }

        const endpoint = subscription.endpoint;

        await fetch("/api/push/unsubscribe", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                workspace: workspace,
                endpoint: endpoint
            })
        });

        await subscription.unsubscribe();

        return "🔕 Content reminders are disabled on this device.";
    } catch (error) {
        console.error("Disable push reminders failed:", error);
        return "❌ Could not disable content reminders.";
    }
}
"""


TEST_PUSH_JS = r"""
async (workspace) => {
    try {
        const response = await fetch("/api/push/test", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({workspace: workspace})
        });

        const result = await response.json();

        if (!response.ok || !result.ok) {
            return "❌ " + (result.message || "Could not send the test notification.");
        }

        return "✅ Test notification sent. Check your notifications.";
    } catch (error) {
        console.error("Test push failed:", error);
        return "❌ Could not send the test notification.";
    }
}
"""


def build_settings_page(
    workspace_name,
    dashboard_output,
    visible=False,
):
    """
    Build Settings, Getting Started, Creator Profile, and reminder controls.

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

        with gr.Accordion("🔔 Content Reminders", open=True):
            gr.Markdown(
                """
                Get push reminders for content on your Channel Coach calendar.

                **Default reminder schedule**
                - 9:00 AM the day before scheduled content
                - 9:00 AM on the scheduled day

                Reminders use this device's timezone. Content already marked
                **Published** is skipped.
                """
            )

            reminder_status = gr.Markdown(
                "Push reminders are currently controlled per device."
            )

            with gr.Row():
                enable_reminders_button = gr.Button(
                    "🔔 Enable Content Reminders",
                    variant="primary",
                )
                test_reminders_button = gr.Button(
                    "🧪 Send Test Notification",
                )
                disable_reminders_button = gr.Button(
                    "🔕 Disable on This Device",
                )

            enable_reminders_button.click(
                fn=None,
                inputs=[workspace_name],
                outputs=[reminder_status],
                js=ENABLE_PUSH_JS,
                show_progress="hidden",
            )

            test_reminders_button.click(
                fn=None,
                inputs=[workspace_name],
                outputs=[reminder_status],
                js=TEST_PUSH_JS,
                show_progress="hidden",
            )

            disable_reminders_button.click(
                fn=None,
                inputs=[workspace_name],
                outputs=[reminder_status],
                js=DISABLE_PUSH_JS,
                show_progress="hidden",
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


