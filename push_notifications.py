import json
import os

from pywebpush import WebPushException, webpush

from database import clean_user_id, supabase, supabase_is_ready


def get_vapid_public_key():
    return (os.getenv("VAPID_PUBLIC_KEY") or "").strip()


def _vapid_private_key():
    return (os.getenv("VAPID_PRIVATE_KEY") or "").strip()


def _vapid_claims():
    contact = (os.getenv("VAPID_CLAIMS_EMAIL") or "").strip()

    if not contact:
        contact = "mailto:admin@example.com"
    elif not contact.startswith("mailto:"):
        contact = f"mailto:{contact}"

    return {"sub": contact}


def push_is_configured():
    return bool(
        supabase_is_ready()
        and get_vapid_public_key()
        and _vapid_private_key()
    )


def save_push_subscription(
    user_id,
    subscription,
    timezone_name="UTC",
):
    safe_user_id = clean_user_id(user_id)
    subscription = subscription or {}

    endpoint = str(
        subscription.get("endpoint") or ""
    ).strip()

    keys = subscription.get("keys") or {}

    p256dh = str(
        keys.get("p256dh") or ""
    ).strip()

    auth = str(
        keys.get("auth") or ""
    ).strip()

    timezone_name = str(
        timezone_name or "UTC"
    ).strip() or "UTC"

    if not endpoint or not p256dh or not auth:
        return (
            False,
            "The browser did not return a complete push subscription.",
        )

    if not supabase_is_ready():
        return (
            False,
            "Push reminders are temporarily unavailable.",
        )

    payload = {
        "user_id": safe_user_id,
        "endpoint": endpoint,
        "p256dh": p256dh,
        "auth": auth,
        "timezone": timezone_name,
        "enabled": True,
    }

    try:
        existing = (
            supabase
            .table("push_subscriptions")
            .select("id")
            .eq("endpoint", endpoint)
            .limit(1)
            .execute()
        )

        if existing.data:
            (
                supabase
                .table("push_subscriptions")
                .update(payload)
                .eq("endpoint", endpoint)
                .execute()
            )
        else:
            (
                supabase
                .table("push_subscriptions")
                .insert(payload)
                .execute()
            )

        return (
            True,
            "Content reminders are enabled on this device.",
        )

    except Exception as exc:
        print(
            f"Push subscription save failed: {exc}"
        )

        return (
            False,
            "Could not save push reminders right now.",
        )


def disable_push_subscription(
    user_id,
    endpoint,
):
    safe_user_id = clean_user_id(user_id)

    endpoint = str(
        endpoint or ""
    ).strip()

    if not endpoint or not supabase_is_ready():
        return (
            False,
            "No active push subscription was found.",
        )

    try:
        (
            supabase
            .table("push_subscriptions")
            .update(
                {"enabled": False}
            )
            .eq("endpoint", endpoint)
            .eq("user_id", safe_user_id)
            .execute()
        )

        return (
            True,
            "Content reminders are disabled on this device.",
        )

    except Exception as exc:
        print(
            f"Push subscription disable failed: {exc}"
        )

        return (
            False,
            "Could not disable reminders right now.",
        )


def _subscription_info(row):
    return {
        "endpoint": row.get("endpoint"),
        "keys": {
            "p256dh": row.get("p256dh"),
            "auth": row.get("auth"),
        },
    }


def send_push_to_row(
    row,
    payload,
):
    if not push_is_configured():
        raise RuntimeError(
            "VAPID or Supabase push configuration is missing."
        )

    return webpush(
        subscription_info=_subscription_info(row),
        data=json.dumps(payload),
        vapid_private_key=_vapid_private_key(),
        vapid_claims=_vapid_claims(),
        ttl=60 * 60 * 24,
    )


def send_test_push(user_id):
    safe_user_id = clean_user_id(user_id)

    if not push_is_configured():
        return (
            False,
            "Push is not fully configured on the server yet.",
        )

    try:
        result = (
            supabase
            .table("push_subscriptions")
            .select("*")
            .eq("user_id", safe_user_id)
            .eq("enabled", True)
            .execute()
        )

        subscriptions = (
            result.data or []
        )

    except Exception as exc:
        print(
            f"Push test subscription load failed: {exc}"
        )

        return (
            False,
            "Could not load your push subscription.",
        )

    if not subscriptions:
        return (
            False,
            "Enable content reminders on this device first.",
        )

    sent = 0

    for row in subscriptions:
        try:
            send_push_to_row(
                row,
                {
                    "title":
                        "🔔 Channel Coach reminders are working",

                    "body":
                        "You’ll get reminders for upcoming content here.",

                    "url": "/",

                    "tag":
                        "channel-coach-test",
                },
            )

            sent += 1

        except WebPushException as exc:
            print(
                f"Push test failed: {exc}"
            )

            if getattr(
                exc,
                "status_code",
                None,
            ) in (404, 410):

                try:
                    (
                        supabase
                        .table("push_subscriptions")
                        .update(
                            {"enabled": False}
                        )
                        .eq(
                            "endpoint",
                            row.get("endpoint"),
                        )
                        .execute()
                    )

                except Exception:
                    pass

        except Exception as exc:
            print(
                f"Push test failed: {exc}"
            )

    if sent:
        return (
            True,
            "Test notification sent.",
        )

    return (
        False,
        "The test notification could not be sent.",
    )

