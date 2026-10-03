# Channel Coach - Settings UI

import gradio as gr

from database import clean_user_id, supabase, supabase_is_ready
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
            return "❌ Notifications were not allowed.";
        }

        const registration = await navigator.serviceWorker.ready;

        const keyResponse = await fetch("/api/push/vapid-public-key");
        const keyData = await keyResponse.json();

        if (!keyResponse.ok || !keyData.public_key) {
            return "❌ Push reminders are not configured on the server yet.";
        }

        function urlBase64ToUint8Array(base64String) {
            const padding = "=".repeat(
                (4 - base64String.length % 4) % 4
            );

            const base64 = (base64String + padding)
                .replace(/-/g, "+")
                .replace(/_/g, "/");

            const rawData = window.atob(base64);

            return Uint8Array.from(
                [...rawData].map(
                    (char) => char.charCodeAt(0)
                )
            );
        }

        const oldSubscription =
            await registration.pushManager.getSubscription();

        if (oldSubscription) {
            try {
                await oldSubscription.unsubscribe();
            } catch (unsubscribeError) {
                console.warn(
                    "Could not remove old subscription:",
                    unsubscribeError
                );
            }
        }

        const subscription =
            await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey:
                    urlBase64ToUint8Array(
                        keyData.public_key
                    ),
            });

        const response = await fetch(
            "/api/push/subscribe",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    workspace: workspace,
                    subscription: subscription.toJSON(),
                    timezone:
                        Intl.DateTimeFormat()
                            .resolvedOptions()
                            .timeZone || "UTC"
                })
            }
        );

        const result = await response.json();

        if (!response.ok || !result.ok) {
            return "❌ " + (
                result.message ||
                "Could not enable reminders."
            );
        }

        return "✅ Content reminders are enabled on this device.";

    } catch (error) {
        console.error(
            "Enable push reminders failed:",
            error
        );

        return (
            "❌ Enable error: " +
            (error.name || "Error") +
            ": " +
            (error.message || String(error))
        );
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


def _format_reminder_time(hour, minute, am_pm):
    try:
        hour = int(hour)
        minute = int(minute)
    except (TypeError, ValueError):
        return None

    if hour < 1 or hour > 12:
        return None

    if minute < 0 or minute > 59:
        return None

    am_pm = str(am_pm or "").strip().upper()

    if am_pm not in ("AM", "PM"):
        return None

    hour_24 = hour % 12

    if am_pm == "PM":
        hour_24 += 12

    return f"{hour_24:02d}:{minute:02d}"


def load_reminder_preferences(workspace):
    """
    Load the saved reminder schedule for the current workspace/user.
    Falls back to 9:00 AM and both reminder days when no saved row exists.
    """
    safe_user_id = clean_user_id(workspace)

    default_values = (
        "9",
        "00",
        "AM",
        "Day before and day of",
        "Choose your reminder schedule, then save it.",
    )

    if not safe_user_id or not supabase_is_ready():
        return default_values

    try:
        result = (
            supabase
            .table("push_subscriptions")
            .select(
                "reminder_time,"
                "remind_day_before,"
                "remind_day_of"
            )
            .eq("user_id", safe_user_id)
            .eq("enabled", True)
            .limit(1)
            .execute()
        )

        rows = result.data or []

        if not rows:
            return default_values

        row = rows[0]

        reminder_time = str(
            row.get("reminder_time") or "09:00"
        ).strip()

        try:
            hour_24_text, minute_text = reminder_time.split(":", 1)
            hour_24 = int(hour_24_text)
            minute = int(minute_text)
        except (TypeError, ValueError):
            hour_24 = 9
            minute = 0

        am_pm = "AM" if hour_24 < 12 else "PM"
        display_hour = hour_24 % 12

        if display_hour == 0:
            display_hour = 12

        reminder_minute = f"{minute:02d}"

        if reminder_minute not in {
            f"{value:02d}"
            for value in range(0, 60, 5)
        }:
            reminder_minute = "00"

        remind_day_before = bool(
            row.get("remind_day_before", True)
        )
        remind_day_of = bool(
            row.get("remind_day_of", True)
        )

        if remind_day_before and remind_day_of:
            reminder_days = "Day before and day of"
        elif remind_day_before:
            reminder_days = "Day before only"
        elif remind_day_of:
            reminder_days = "Day of only"
        else:
            reminder_days = "Day before and day of"

        status = (
            f"✅ Saved reminder schedule loaded: "
            f"{display_hour}:{reminder_minute} "
            f"{am_pm} ({reminder_days.lower()})."
        )

        return (
            str(display_hour),
            reminder_minute,
            am_pm,
            reminder_days,
            status,
        )

    except Exception as exc:
        print(
            f"Reminder preference load failed: {exc}",
            flush=True,
        )
        return default_values


def save_reminder_preferences(
    workspace,
    reminder_hour,
    reminder_minute,
    reminder_am_pm,
    reminder_days,
):
    safe_user_id = clean_user_id(workspace)

    if not safe_user_id:
        return "❌ Log in before saving reminder preferences."

    if not supabase_is_ready():
        return "❌ Reminder preferences are temporarily unavailable."

    reminder_time = _format_reminder_time(
        reminder_hour,
        reminder_minute,
        reminder_am_pm,
    )

    if not reminder_time:
        return "❌ Choose a valid reminder time."

    reminder_days = str(reminder_days or "").strip()

    if reminder_days == "Day before only":
        remind_day_before = True
        remind_day_of = False
        schedule_text = "day before"

    elif reminder_days == "Day of only":
        remind_day_before = False
        remind_day_of = True
        schedule_text = "day of"

    else:
        remind_day_before = True
        remind_day_of = True
        schedule_text = "day before and day of"

    try:
        result = (
            supabase
            .table("push_subscriptions")
            .select("id")
            .eq("user_id", safe_user_id)
            .eq("enabled", True)
            .execute()
        )

        rows = result.data or []

        if not rows:
            return (
                "❌ Enable Content Reminders on this device first, "
                "then save your reminder preferences."
            )

        (
            supabase
            .table("push_subscriptions")
            .update(
                {
                    "reminder_time": reminder_time,
                    "remind_day_before": remind_day_before,
                    "remind_day_of": remind_day_of,
                }
            )
            .eq("user_id", safe_user_id)
            .eq("enabled", True)
            .execute()
        )

        display_hour = int(reminder_hour)
        display_minute = int(reminder_minute)

        return (
            f"✅ Reminder preferences saved: "
            f"{display_hour}:{display_minute:02d} "
            f"{str(reminder_am_pm).upper()} "
            f"({schedule_text})."
        )

    except Exception as exc:
        print(
            f"Reminder preference save failed: {exc}",
            flush=True,
        )

        return (
            "❌ Could not save reminder preferences. "
            "Make sure the reminder preference columns were added in Supabase."
        )


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

                Choose **when** you want reminders and **which days** you want
                them. Reminder times use the timezone saved for your device.
                Content already marked **Published** will be skipped.
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

            gr.Markdown("### ⏰ Reminder Schedule")

            with gr.Row():
                reminder_hour = gr.Dropdown(
                    choices=[str(value) for value in range(1, 13)],
                    value="9",
                    label="Hour",
                    interactive=True,
                )

                reminder_minute = gr.Dropdown(
                    choices=[
                        f"{value:02d}"
                        for value in range(0, 60, 5)
                    ],
                    value="00",
                    label="Minute",
                    interactive=True,
                )

                reminder_am_pm = gr.Dropdown(
                    choices=["AM", "PM"],
                    value="AM",
                    label="AM / PM",
                    interactive=True,
                )

            reminder_days = gr.Dropdown(
                choices=[
                    "Day before and day of",
                    "Day before only",
                    "Day of only",
                ],
                value="Day before and day of",
                label="When should Channel Coach remind you?",
                interactive=True,
            )

            save_reminder_preferences_button = gr.Button(
                "💾 Save Reminder Preferences",
                variant="primary",
            )

            reminder_preferences_status = gr.Markdown(
                "Choose your reminder schedule, then save it."
            )

            save_reminder_preferences_button.click(
                save_reminder_preferences,
                inputs=[
                    workspace_name,
                    reminder_hour,
                    reminder_minute,
                    reminder_am_pm,
                    reminder_days,
                ],
                outputs=[reminder_preferences_status],
                show_progress="hidden",
            )

            # Whenever login/restore changes the active workspace, refresh
            # the reminder controls from Supabase automatically.
            workspace_name.change(
                load_reminder_preferences,
                inputs=[workspace_name],
                outputs=[
                    reminder_hour,
                    reminder_minute,
                    reminder_am_pm,
                    reminder_days,
                    reminder_preferences_status,
                ],
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





