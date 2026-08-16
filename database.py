import os
import json
import re
from dotenv import load_dotenv

# =========================
# OPTIONAL SUPABASE IMPORT
# =========================
try:
    from supabase import create_client, Client
    SUPABASE_IMPORT_ERROR = None
except Exception as e:
    create_client = None
    Client = None
    SUPABASE_IMPORT_ERROR = str(e)

load_dotenv()

# =========================
# SUPABASE DATABASE
# =========================
# Render environment variables supported:
#
# SUPABASE_URL
#
# And either:
# SUPABASE_ANON_KEY
# or:
# SUPABASE_KEY
#
# The app accepts both key names so you do not have to rename an
# existing Render environment variable.

SUPABASE_URL = os.getenv("SUPABASE_URL")

SUPABASE_KEY = (
    os.getenv("SUPABASE_ANON_KEY")
    or os.getenv("SUPABASE_KEY")
)

supabase = None
SUPABASE_CONNECTION_ERROR = None

if create_client is None:
    SUPABASE_CONNECTION_ERROR = (
        f"Supabase package could not be imported: {SUPABASE_IMPORT_ERROR}"
    )
elif not SUPABASE_URL:
    SUPABASE_CONNECTION_ERROR = "SUPABASE_URL is missing."
elif not SUPABASE_KEY:
    SUPABASE_CONNECTION_ERROR = (
        "Supabase key is missing. Set SUPABASE_ANON_KEY or SUPABASE_KEY."
    )
else:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        SUPABASE_CONNECTION_ERROR = f"Could not create Supabase client: {e}"


def supabase_is_ready():
    return supabase is not None


def supabase_status():
    """
    Returns a safe diagnostic string without exposing secrets.
    Useful for Render logs and troubleshooting.
    """
    if supabase_is_ready():
        return "Supabase configured and ready."

    return SUPABASE_CONNECTION_ERROR or "Supabase is not configured."


# Safe startup diagnostics.
# These never print the actual URL or key values.
print("Supabase package available:", create_client is not None)
print("SUPABASE_URL configured:", bool(SUPABASE_URL))
print("Supabase key configured:", bool(SUPABASE_KEY))
print("Supabase ready:", supabase_is_ready())

if not supabase_is_ready():
    print("Supabase status:", supabase_status())


# =========================
# USER / WORKSPACE HELPERS
# =========================
def clean_user_id(user_id="main"):
    """
    Converts a workspace name or user ID into a safe database ID.

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
# Render's local filesystem may not be permanent between restarts
# or deploys. This fallback keeps the app usable when Supabase is
# unavailable, but Supabase should be used for permanent storage.

DATA_DIR = os.getenv("DATA_DIR", ".")
os.makedirs(DATA_DIR, exist_ok=True)


def data_file(name):
    return os.path.join(DATA_DIR, name)


def user_data_file(name, user_id="main"):
    """
    Creates a user-specific local fallback file name.

    Example:
    creator_profile.json + nikki
    -> creator_profile_nikki.json
    """
    safe_user_id = clean_user_id(user_id)
    root, ext = os.path.splitext(name)

    if not ext:
        ext = ".json"

    return os.path.join(
        DATA_DIR,
        f"{root}_{safe_user_id}{ext}"
    )


def load_json_file(file_path, default_value):
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"Local JSON load error for {file_path}: {e}")

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
def load_creator_profile_record(
    default_profile,
    profile_file,
    user_id="main"
):
    """
    Loads the creator profile for one workspace/user.

    Storage order:
    1. Supabase
    2. User-specific local JSON fallback
    3. Older shared local profile file for workspace "main"
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

                if isinstance(saved_profile, dict):
                    profile.update(saved_profile)

                return profile

        except Exception as e:
            print(
                f"Supabase creator profile load failed "
                f"for {safe_user_id}: {e}"
            )

    fallback_file = user_data_file(
        os.path.basename(profile_file),
        safe_user_id
    )

    saved_profile = load_json_file(
        fallback_file,
        {}
    )

    # Backward compatibility for older local installs.
    if not saved_profile and safe_user_id == "main":
        saved_profile = load_json_file(
            profile_file,
            {}
        )

    profile = default_profile.copy()

    if isinstance(saved_profile, dict):
        profile.update(saved_profile)

    return profile


def save_creator_profile_record(
    profile,
    profile_file,
    user_id="main"
):
    """
    Saves the creator profile for one workspace/user.

    Storage order:
    1. Supabase
    2. User-specific local JSON fallback
    """
    safe_user_id = clean_user_id(user_id)
    supabase_error = None

    if supabase_is_ready():
        try:
            (
                supabase
                .table("creator_profiles")
                .upsert(
                    {
                        "id": safe_user_id,
                        "data": profile
                    }
                )
                .execute()
            )

            return (
                "✅ Creator profile saved for workspace: "
                f"{safe_user_id}"
            )

        except Exception as e:
            supabase_error = str(e)
            print(
                f"Supabase creator profile save failed "
                f"for {safe_user_id}: {e}"
            )
    else:
        supabase_error = supabase_status()

    try:
        fallback_file = user_data_file(
            os.path.basename(profile_file),
            safe_user_id
        )

        save_json_file(
            fallback_file,
            profile
        )

        return (
            "✅ Creator profile saved locally for workspace: "
            f"{safe_user_id}. "
            f"Supabase fallback note: {supabase_error}"
        )

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
        return (
            "❌ Supabase is not configured. "
            f"Calendar item was not saved. {supabase_status()}"
        )

    try:
        (
            supabase
            .table("content_calendar")
            .insert(
                {
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
                }
            )
            .execute()
        )

        return (
            "✅ Calendar item saved for workspace: "
            f"{safe_user_id}"
        )

    except Exception as e:
        print(
            f"Supabase calendar insert failed "
            f"for {safe_user_id}: {e}"
        )
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

    except Exception as e:
        print(
            f"Supabase calendar load failed "
            f"for {safe_user_id}: {e}"
        )
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
        return (
            "❌ Supabase is not configured. "
            f"Calendar item was not updated. {supabase_status()}"
        )

    try:
        (
            supabase
            .table("content_calendar")
            .update(
                {
                    "title": title,
                    "platform": platform,
                    "content_type": content_type,
                    "status": status,
                    "publish_date": publish_date or None,
                    "publish_time": publish_time or None,
                    "priority": priority,
                    "notes": notes,
                    "tags": tags
                }
            )
            .eq("id", item_id)
            .eq("user_id", safe_user_id)
            .execute()
        )

        return "✅ Calendar item updated!"

    except Exception as e:
        print(
            f"Supabase calendar update failed "
            f"for {safe_user_id}: {e}"
        )
        return f"❌ Could not update calendar item: {e}"


def delete_calendar_item(
    item_id,
    user_id="main"
):
    safe_user_id = clean_user_id(user_id)

    if not supabase_is_ready():
        return (
            "❌ Supabase is not configured. "
            f"Calendar item was not deleted. {supabase_status()}"
        )

    try:
        (
            supabase
            .table("content_calendar")
            .delete()
            .eq("id", item_id)
            .eq("user_id", safe_user_id)
            .execute()
        )

        return "✅ Calendar item deleted!"

    except Exception as e:
        print(
            f"Supabase calendar delete failed "
            f"for {safe_user_id}: {e}"
        )
        return f"❌ Could not delete calendar item: {e}"

