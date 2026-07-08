import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL not found in .env")

if not SUPABASE_ANON_KEY:
    raise ValueError("SUPABASE_ANON_KEY not found in .env")

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


def signup_user(email, password):
    try:
        response = supabase.auth.sign_up(
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


def login_user(email, password):
    try:
        response = supabase.auth.sign_in_with_password(
            {
                "email": email,
                "password": password,
            }
        )

        if response.user:
            return (
                f"✅ Welcome {response.user.email}!",
                response.user.id,
            )

        return "❌ Login failed.", None

    except Exception as e:
        return f"❌ {e}", None


def logout_user():
    try:
        supabase.auth.sign_out()
        return "✅ Logged out."
    except Exception as e:
        return f"❌ {e}"
