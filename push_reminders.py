import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pywebpush import WebPushException

from database import clean_user_id, supabase, supabase_is_ready
from push_notifications import send_push_to_row


def _parse_reminder_time(value):
    value = str(value or "").strip()
    try:
        hour_text, minute_text = value.split(":", 1)
        hour = int(hour_text)
        minute = int(minute_text)
    except (ValueError, TypeError):
        return None
    if hour < 0 or hour > 23 or minute < 0 or minute > 59:
        return None
    return hour, minute


def _local_now(timezone_name, now_utc):
    timezone_name = str(timezone_name or "UTC").strip() or "UTC"
    try:
        zone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        zone = timezone.utc
    return now_utc.astimezone(zone)


def _subscription_id(subscription):
    return str(
        subscription.get("id")
        or subscription.get("endpoint")
        or "device"
    )


def _subscription_delivery_key(subscription, item):
    subscription_id = _subscription_id(subscription)
    item_id = str(item.get("id") or "content")
    return f"{item_id}:{subscription_id}"


def _overdue_delivery_key(subscription):
    return f"overdue-summary:{_subscription_id(subscription)}"


def _already_sent(user_id, delivery_key, reminder_type, reminder_date):
    result = (
        supabase.table("push_reminder_log")
        .select("id")
        .eq("user_id", user_id)
        .eq("content_item_id", delivery_key)
        .eq("reminder_type", reminder_type)
        .eq("reminder_date", reminder_date)
        .limit(1)
        .execute()
    )
    return bool(result.data)


def _record_sent(user_id, delivery_key, reminder_type, reminder_date):
    (
        supabase.table("push_reminder_log")
        .insert(
            {
                "user_id": user_id,
                "content_item_id": delivery_key,
                "reminder_type": reminder_type,
                "reminder_date": reminder_date,
            }
        )
        .execute()
    )


def _disable_expired_subscription(subscription):
    endpoint = str(subscription.get("endpoint") or "").strip()
    if not endpoint:
        return
    try:
        (
            supabase.table("push_subscriptions")
            .update({"enabled": False})
            .eq("endpoint", endpoint)
            .execute()
        )
    except Exception as exc:
        print(f"Could not disable expired subscription: {exc}", flush=True)


def _calendar_items_for_date(user_id, publish_date):
    result = (
        supabase.table("content_calendar")
        .select("*")
        .eq("user_id", user_id)
        .eq("publish_date", publish_date)
        .execute()
    )
    items = result.data or []
    return [
        item for item in items
        if str(item.get("status") or "").strip().lower() != "published"
    ]


def _overdue_calendar_items(user_id, today):
    result = (
        supabase.table("content_calendar")
        .select("*")
        .eq("user_id", user_id)
        .lt("publish_date", today.isoformat())
        .order("publish_date")
        .execute()
    )
    items = result.data or []
    return [
        item for item in items
        if str(item.get("status") or "").strip().lower() != "published"
    ]


def _payload_for(item, reminder_type):
    title = str(item.get("title") or "Scheduled content").strip()
    platform = str(item.get("platform") or "").strip()

    if reminder_type == "day_before":
        heading = "📅 Content reminder for tomorrow"
        body = f"Tomorrow: {title}"
    else:
        heading = "🔔 Content reminder for today"
        body = f"Today: {title}"

    if platform:
        body += f" • {platform}"

    return {
        "title": heading,
        "body": body,
        "url": "/",
        "tag": f"channel-coach-{reminder_type}-{item.get('id') or 'content'}",
    }


def _overdue_payload(items):
    count = len(items)
    oldest = items[0] if items else {}
    oldest_title = str(oldest.get("title") or "an overdue project").strip()

    if count == 1:
        heading = "⚠️ You have 1 overdue project"
        body = f"{oldest_title} is overdue. Open Channel Coach to get caught up."
    else:
        heading = f"⚠️ You have {count} overdue projects"
        body = (
            f"Your oldest overdue project is {oldest_title}. "
            "Open Channel Coach to get caught up."
        )

    return {
        "title": heading,
        "body": body,
        "url": "/",
        "tag": "channel-coach-overdue-summary",
    }


def _send_for_date(subscription, user_id, target_date, reminder_type):
    publish_date = target_date.isoformat()
    items = _calendar_items_for_date(user_id, publish_date)
    sent = 0

    for item in items:
        delivery_key = _subscription_delivery_key(subscription, item)
        try:
            if _already_sent(
                user_id, delivery_key, reminder_type, publish_date
            ):
                continue

            send_push_to_row(subscription, _payload_for(item, reminder_type))
            _record_sent(
                user_id, delivery_key, reminder_type, publish_date
            )
            sent += 1
            print(
                "Reminder sent:",
                user_id,
                reminder_type,
                publish_date,
                item.get("title"),
                flush=True,
            )

        except WebPushException as exc:
            response = getattr(exc, "response", None)
            status_code = getattr(response, "status_code", None)
            print(
                "Push reminder failed:",
                user_id,
                item.get("title"),
                exc,
                flush=True,
            )
            if status_code in (404, 410):
                _disable_expired_subscription(subscription)

        except Exception as exc:
            print(
                "Reminder processing failed:",
                user_id,
                item.get("title"),
                f"{type(exc).__name__}: {exc}",
                flush=True,
            )

    return sent


def _send_overdue_summary(subscription, user_id, local_today):
    reminder_date = local_today.isoformat()
    delivery_key = _overdue_delivery_key(subscription)

    try:
        if _already_sent(
            user_id, delivery_key, "overdue", reminder_date
        ):
            return 0

        items = _overdue_calendar_items(user_id, local_today)
        if not items:
            return 0

        send_push_to_row(subscription, _overdue_payload(items))
        _record_sent(
            user_id, delivery_key, "overdue", reminder_date
        )

        print(
            "Overdue summary sent:",
            user_id,
            reminder_date,
            f"{len(items)} overdue project(s)",
            flush=True,
        )
        return 1

    except WebPushException as exc:
        response = getattr(exc, "response", None)
        status_code = getattr(response, "status_code", None)
        print("Overdue push reminder failed:", user_id, exc, flush=True)
        if status_code in (404, 410):
            _disable_expired_subscription(subscription)

    except Exception as exc:
        print(
            "Overdue reminder processing failed:",
            user_id,
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )

    return 0


def run_reminders():
    if not supabase_is_ready():
        print(
            "Push reminder worker stopped: Supabase is unavailable.",
            flush=True,
        )
        return 1

    now_utc = datetime.now(timezone.utc)

    try:
        result = (
            supabase.table("push_subscriptions")
            .select("*")
            .eq("enabled", True)
            .execute()
        )
    except Exception as exc:
        print(f"Could not load push subscriptions: {exc}", flush=True)
        return 1

    subscriptions = result.data or []

    print(
        f"Push reminder worker checking {len(subscriptions)} enabled device(s).",
        flush=True,
    )

    total_sent = 0

    for subscription in subscriptions:
        user_id = clean_user_id(subscription.get("user_id"))

        parsed_time = _parse_reminder_time(
            subscription.get("reminder_time") or "09:00"
        )
        if not parsed_time:
            print(f"Skipping {user_id}: invalid reminder_time.", flush=True)
            continue

        reminder_hour, reminder_minute = parsed_time
        local_now = _local_now(subscription.get("timezone"), now_utc)

        if (
            local_now.hour != reminder_hour
            or local_now.minute != reminder_minute
        ):
            continue

        # Send at most one overdue summary per day/device at the
        # user's normal reminder time.
        total_sent += _send_overdue_summary(
            subscription,
            user_id,
            local_now.date(),
        )

        if bool(subscription.get("remind_day_before", True)):
            total_sent += _send_for_date(
                subscription,
                user_id,
                local_now.date() + timedelta(days=1),
                "day_before",
            )

        if bool(subscription.get("remind_day_of", True)):
            total_sent += _send_for_date(
                subscription,
                user_id,
                local_now.date(),
                "day_of",
            )

    print(
        f"Push reminder worker finished. Sent {total_sent} reminder(s).",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    sys.exit(run_reminders())
