import os
import json
import re
from dotenv import load_dotenv

try:
    from supabase import create_client, Client
except Exception:
    create_client = None
    Client = None

load_dotenv()

# =========================
# SUPABASE DATABASE
# =========================
# Add these environment variables in Render:
# SUPABASE_URL = your Supabase project URL
# SUPABASE_KEY = your Supabase anon/public key
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = None
if create_client and SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        supabase = None


def supabase_is_ready():
    return supabase is not None


# =========================
# USER / WORKSPACE HELPERS
# =========================
def clean_user_id(user_id="main"):
    """
    Converts a workspace name into a safe database ID.
    Examples:
    - "Nikki" -> "nikki"
    - "Retro Gamer 92" -> "retro-gamer-92"
    """
    raw = str(user_id or "main").strip().lower()
    raw = re.sub(r"[^a-z0-9_-]+", "-", raw)
    raw = raw.strip("-_")
    return raw or "main"


# =========================
# LOCAL FALLBACK STORAGE
# =========================
# Render free storage is not permanent, but this keeps the app usable if
# Supabase is missing or temporarily unavailable.
DATA_DIR = os.getenv("DATA_DIR", ".")
os.makedirs(DATA_DIR, exist_ok=True)


def data_file(name):
    return os.path.join(DATA_DIR, name)


def user_data_file(name, user_id="main"):
    """
    Creates a user-specific fallback file name.
    Example: creator_profile.json + nikki -> creator_profile_nikki.json
    """
    safe_user_id = clean_user_id(user_id)
    root, ext = os.path.splitext(name)
    if not ext:
        ext = ".json"
    return os.path.join(DATA_DIR, f"{root}_{safe_user_id}{ext}")


def load_json_file(file_path, default_value):
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass

    return default_value


def save_json_file(file_path, data):
    file_dir = os.path.dirname(file_path)

    if file_dir:
        os.makedirs(file_dir, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# =========================
# CREATOR PROFILE STORAGE
# =========================
def load_creator_profile_record(default_profile, profile_file, user_id="main"):
    """
    Loads the creator profile for one workspace/user from Supabase first.
    If Supabase is unavailable, falls back to a user-specific local JSON file.

    Backward compatible:
    - If user_id is not provided, it still uses "main".
    """
    safe_user_id = clean_user_id(user_id)

    if supabase_is_ready():
        try:
            result = (
                supabase
                .table("creator_profiles")
                .select("data")
                .eq("id", safe_user_id)
                .limit(1)
                .execute()
            )

            if result.data:
                saved_profile = result.data[0].get("data") or {}
                profile = default_profile.copy()
                profile.update(saved_profile)
                return profile

        except Exception:
            pass

    fallback_file = user_data_file(os.path.basename(profile_file), safe_user_id)
    saved_profile = load_json_file(fallback_file, {})

    # Backward compatibility for older local installs using the shared file.
    if not saved_profile and safe_user_id == "main":
        saved_profile = load_json_file(profile_file, {})

    profile = default_profile.copy()

    if isinstance(saved_profile, dict):
        profile.update(saved_profile)

    return profile


def save_creator_profile_record(profile, profile_file, user_id="main"):
    """
    Saves the creator profile for one workspace/user to Supabase first.
    If Supabase is unavailable, falls back to a user-specific local JSON file.
    """
    safe_user_id = clean_user_id(user_id)
    supabase_error = None

    if supabase_is_ready():
        try:
            (
                supabase
                .table("creator_profiles")
                .upsert({
                    "id": safe_user_id,
                    "data": profile
                })
                .execute()
            )

            return f"✅ Creator profile saved for workspace: {safe_user_id}"

        except Exception as e:
            supabase_error = str(e)
    else:
        supabase_error = "Supabase is not configured."

    try:
        fallback_file = user_data_file(os.path.basename(profile_file), safe_user_id)
        save_json_file(fallback_file, profile)
        return f"✅ Creator profile saved locally for workspace: {safe_user_id}. Supabase fallback note: {supabase_error}"

    except Exception as e:
        return f"❌ Could not save creator profile: {e}"


# =========================
# CONTENT CALENDAR STORAGE
# =========================
def add_calendar_item(
    title,
    platform,
    content_type,
    status,
    publish_date,
    publish_time,
    priority,
    notes,
    tags,
    user_id="main"
):
    safe_user_id = clean_user_id(user_id)

    if not supabase_is_ready():
        return "❌ Supabase is not configured. Calendar item was not saved."

    try:
        supabase.table("content_calendar").insert({
            "user_id": safe_user_id,
            "title": title,
            "platform": platform,
            "content_type": content_type,
            "status": status,
            "publish_date": publish_date or None,
            "publish_time": publish_time or None,
            "priority": priority,
            "notes": notes,
            "tags": tags
        }).execute()

        return f"✅ Calendar item saved for workspace: {safe_user_id}"

    except Exception as e:
        return f"❌ Could not save calendar item: {e}"


def get_calendar_items(user_id="main"):
    safe_user_id = clean_user_id(user_id)

    if not supabase_is_ready():
        return []

    try:
        result = (
            supabase
            .table("content_calendar")
            .select("*")
            .eq("user_id", safe_user_id)
            .order("publish_date", desc=False)
            .execute()
        )

        return result.data or []

    except Exception:
        return []


def update_calendar_item(
    item_id,
    title,
    platform,
    content_type,
    status,
    publish_date,
    publish_time,
    priority,
    notes,
    tags,
    user_id="main"
):
    safe_user_id = clean_user_id(user_id)

    if not supabase_is_ready():
        return "❌ Supabase is not configured. Calendar item was not updated."

    try:
        supabase.table("content_calendar").update({
            "title": title,
            "platform": platform,
            "content_type": content_type,
            "status": status,
            "publish_date": publish_date or None,
            "publish_time": publish_time or None,
            "priority": priority,
            "notes": notes,
            "tags": tags
        }).eq("id", item_id).eq("user_id", safe_user_id).execute()

        return "✅ Calendar item updated!"

    except Exception as e:
        return f"❌ Could not update calendar item: {e}"


def delete_calendar_item(item_id, user_id="main"):
    safe_user_id = clean_user_id(user_id)

    if not supabase_is_ready():
        return "❌ Supabase is not configured. Calendar item was not deleted."

    try:
        supabase.table("content_calendar").delete().eq("id", item_id).eq("user_id", safe_user_id).execute()
        return "✅ Calendar item deleted!"

    except Exception as e:
        return f"❌ Could not delete calendar item: {e}"
