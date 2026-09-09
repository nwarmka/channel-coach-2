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
    Create a separate Supabase client for each auth operation.

    This prevents one visitor's authenticated Supabase session from being
    shared with another visitor on the Render server.
    """
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


def empty_saved_session() -> dict[str, str]:
    return {
        "access_token": "",
        "refresh_token": "",
        "user_id": "",
        "email": "",
    }


def _error_text(error: Exception) -> str:
    return str(error or "").strip()


def _friendly_auth_error(error: Exception, action: str = "login") -> str:
    """
    Convert common Supabase/auth errors into user-facing messages without
    dumping internal exception details into the UI.
    """
    raw = _error_text(error)
    lowered = raw.lower()

    if "invalid login credentials" in lowered:
        return "❌ Incorrect email or password."

    if "email not confirmed" in lowered:
        return "❌ Please verify your email before logging in."

    if "user already registered" in lowered or "already been registered" in lowered:
        return "❌ An account with that email already exists."

    if "password should be at least" in lowered or "weak password" in lowered:
        return "❌ That password is too weak. Please choose a stronger password."

    if "rate limit" in lowered or "too many requests" in lowered or "429" in lowered:
        return "❌ Too many attempts. Please wait a little while and try again."

    network_markers = (
        "timed out",
        "timeout",
        "connection",
        "network",
        "temporarily unavailable",
        "service unavailable",
        "502",
        "503",
        "504",
    )
    if any(marker in lowered for marker in network_markers):
        return "❌ Channel Coach cannot reach the login service right now. Please try again shortly."

    if action == "signup":
        return "❌ We couldn't create the account right now. Please try again."

    if action == "reset":
        return "❌ We couldn't send the password-reset email right now. Please try again."

    return "❌ We couldn't sign you in right now. Please try again."


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
            # Supabase may intentionally avoid revealing whether an email already
            # exists depending on the project's email-confirmation settings.
            return (
                "✅ Check your email. If this address can be registered, "
                "Supabase will send the next step."
            )

        return "❌ Unable to create account."

    except Exception as e:
        return _friendly_auth_error(e, action="signup")


def login_user(
    email: str,
    password: str,
) -> tuple[str, str | None, dict[str, str]]:
    """
    Log in and return:
        user-facing message
        Supabase user ID
        serializable session payload for device persistence
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
            f"✅ Welcome {response.user.email or email}!",
            response.user.id,
            saved_session,
        )

    except Exception as e:
        return (
            _friendly_auth_error(e, action="login"),
            None,
            empty_saved_session(),
        )


def restore_saved_session(
    saved_session: Any,
) -> tuple[str, str | None, dict[str, str]]:
    """
    Restore a saved Supabase session.

    set_session() refreshes an expired access token when the refresh token is
    still valid. If either token is no longer usable, the device's saved login
    is cleared and the user is asked to sign in again.
    """
    if not isinstance(saved_session, dict):
        return (
            "Please log in.",
            None,
            empty_saved_session(),
        )

    access_token = str(saved_session.get("access_token", "") or "")
    refresh_token = str(saved_session.get("refresh_token", "") or "")

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

        # Validate the authenticated user against Supabase rather than trusting
        # only the locally stored user_id.
        verified = client.auth.get_user()
        verified_user = getattr(verified, "user", None)

        if not verified_user:
            return (
                "Your saved login has expired. Please log in again.",
                None,
                empty_saved_session(),
            )

        refreshed_session = {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "user_id": verified_user.id,
            "email": verified_user.email or saved_session.get("email", ""),
        }

        return (
            f"✅ Welcome back {verified_user.email or ''}!",
            verified_user.id,
            refreshed_session,
        )

    except Exception:
        return (
            "Your saved login has expired. Please log in again.",
            None,
            empty_saved_session(),
        )


def request_password_reset(
    email: str,
    redirect_to: str | None = None,
) -> str:
    """
    Ask Supabase to send a password recovery email.

    The redirect URL must also be allowed in Supabase Auth redirect settings.
    """
    email = (email or "").strip()

    if not email:
        return "❌ Enter your email address first."

    try:
        client = create_supabase_client()

        if redirect_to:
            client.auth.reset_password_for_email(
                email,
                {"redirect_to": redirect_to},
            )
        else:
            client.auth.reset_password_for_email(email)

        # Keep this deliberately non-enumerating.
        return (
            "✅ If an account exists for that email, "
            "a password-reset message has been sent."
        )

    except Exception as e:
        return _friendly_auth_error(e, action="reset")


def update_password_from_session(
    saved_session: Any,
    new_password: str,
) -> tuple[str, dict[str, str]]:
    """
    Update the password for an already authenticated recovery/session context.

    This is ready for the eventual reset callback/native app flow. The current
    PWA still needs its recovery-link callback wired in app.py before this can
    complete an emailed reset end-to-end.
    """
    new_password = new_password or ""

    if len(new_password) < 8:
        return (
            "❌ Use a password with at least 8 characters.",
            empty_saved_session(),
        )

    if not isinstance(saved_session, dict):
        return (
            "❌ Your password-reset session is no longer valid.",
            empty_saved_session(),
        )

    access_token = str(saved_session.get("access_token", "") or "")
    refresh_token = str(saved_session.get("refresh_token", "") or "")

    if not access_token or not refresh_token:
        return (
            "❌ Your password-reset session is no longer valid.",
            empty_saved_session(),
        )

    try:
        client = create_supabase_client()
        session_response = client.auth.set_session(access_token, refresh_token)

        if not session_response.user or not session_response.session:
            return (
                "❌ Your password-reset session has expired.",
                empty_saved_session(),
            )

        client.auth.update_user({"password": new_password})

        refreshed = {
            "access_token": session_response.session.access_token,
            "refresh_token": session_response.session.refresh_token,
            "user_id": session_response.user.id,
            "email": session_response.user.email or "",
        }

        return (
            "✅ Password updated.",
            refreshed,
        )

    except Exception as e:
        return (
            _friendly_auth_error(e, action="reset"),
            empty_saved_session(),
        )


def logout_user(
    saved_session: Any,
) -> tuple[str, None, dict[str, str]]:
    """
    Sign out remotely when possible, but ALWAYS clear the local saved tokens.
    """
    try:
        if isinstance(saved_session, dict):
            access_token = str(saved_session.get("access_token", "") or "")
            refresh_token = str(saved_session.get("refresh_token", "") or "")

            if access_token and refresh_token:
                client = create_supabase_client()
                client.auth.set_session(access_token, refresh_token)
                client.auth.sign_out()

    except Exception:
        # Local logout must still succeed during a Supabase/network outage.
        pass

    return (
        "✅ Logged out.",
        None,
        empty_saved_session(),
    )


