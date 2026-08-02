import os
from typing import Any

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL not found in environment variables.")

if not SUPABASE_ANON_KEY:
    raise ValueError("SUPABASE_ANON_KEY not found in environment variables.")


def create_supabase_client() -> Client:
    """
    Create a separate Supabase client instead of sharing one logged-in
    authentication session between every visitor using the Render server.
    """
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


def empty_saved_session() -> dict[str, str]:
    return {
        "access_token": "",
        "refresh_token": "",
        "user_id": "",
        "email": "",
    }


def signup_user(email: str, password: str) -> str:
    email = (email or "").strip()
    password = password or ""

    if not email or not password:
        return "❌ Enter your email and password."

    try:
        client = create_supabase_client()

        response = client.auth.sign_up(
            {
                "email": email,
                "password": password,
            }
        )

        if response.user:
            return "✅ Account created! Check your email to verify your account."

        return "❌ Unable to create account."

    except Exception as e:
        return f"❌ {e}"


def login_user(
    email: str,
    password: str,
) -> tuple[str, str | None, dict[str, str]]:
    """
    Log the user in and return session information that can be saved in
    gr.BrowserState.

    Returns:
        login message
        user ID
        saved browser session
    """
    email = (email or "").strip()
    password = password or ""

    if not email or not password:
        return (
            "❌ Enter your email and password.",
            None,
            empty_saved_session(),
        )

    try:
        client = create_supabase_client()

        response = client.auth.sign_in_with_password(
            {
                "email": email,
                "password": password,
            }
        )

        if not response.user or not response.session:
            return (
                "❌ Login failed.",
                None,
                empty_saved_session(),
            )

        saved_session = {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "user_id": response.user.id,
            "email": response.user.email or email,
        }

        return (
            f"✅ Welcome {response.user.email}!",
            response.user.id,
            saved_session,
        )

    except Exception as e:
        return (
            f"❌ {e}",
            None,
            empty_saved_session(),
        )


def restore_saved_session(
    saved_session: Any,
) -> tuple[str, str | None, dict[str, str]]:
    """
    Restore a login from the access and refresh tokens saved on this browser.

    Supabase will refresh an expired access token when set_session() is called
    with a valid refresh token.
    """
    if not isinstance(saved_session, dict):
        return (
            "Please log in.",
            None,
            empty_saved_session(),
        )

    access_token = saved_session.get("access_token", "")
    refresh_token = saved_session.get("refresh_token", "")

    if not access_token or not refresh_token:
        return (
            "Please log in.",
            None,
            empty_saved_session(),
        )

    try:
        client = create_supabase_client()

        response = client.auth.set_session(
            access_token,
            refresh_token,
        )

        if not response.user or not response.session:
            return (
                "Your saved login has expired. Please log in again.",
                None,
                empty_saved_session(),
            )

        refreshed_session = {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "user_id": response.user.id,
            "email": response.user.email or saved_session.get("email", ""),
        }

        return (
            f"✅ Welcome back {response.user.email}!",
            response.user.id,
            refreshed_session,
        )

    except Exception:
        return (
            "Your saved login has expired. Please log in again.",
            None,
            empty_saved_session(),
        )


def logout_user(
    saved_session: Any,
) -> tuple[str, None, dict[str, str]]:
    """
    Sign out the saved Supabase session and clear the browser's saved tokens.
    """
    try:
        if isinstance(saved_session, dict):
            access_token = saved_session.get("access_token", "")
            refresh_token = saved_session.get("refresh_token", "")

            if access_token and refresh_token:
                client = create_supabase_client()
                client.auth.set_session(access_token, refresh_token)
                client.auth.sign_out()

    except Exception:
        # Still clear the browser session even if the remote sign-out fails.
        pass

    return (
        "✅ Logged out.",
        None,
        empty_saved_session(),
    )

