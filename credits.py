import os
import uuid

from dotenv import load_dotenv

try:
    from supabase import create_client
except Exception:
    create_client = None

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

DEFAULT_STARTING_CREDITS = int(
    os.getenv("CHANNEL_COACH_STARTING_CREDITS", "100")
)

_credit_client = None


def _client():
    """
    Backend-only Supabase client for credit mutations.

    IMPORTANT:
    SUPABASE_SERVICE_ROLE_KEY belongs only in Render/server environment
    variables. Never put it in browser code, GitHub, or a mobile app.
    """
    global _credit_client

    if _credit_client is not None:
        return _credit_client

    if not create_client or not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise RuntimeError(
            "Credit system is not configured. Add SUPABASE_URL and "
            "SUPABASE_SERVICE_ROLE_KEY to the Render environment."
        )

    _credit_client = create_client(
        SUPABASE_URL,
        SUPABASE_SERVICE_ROLE_KEY,
    )
    return _credit_client


def _valid_user_id(user_id):
    """
    Credit accounts must belong to a real Supabase Auth UUID.
    """
    try:
        return str(uuid.UUID(str(user_id)))
    except (ValueError, TypeError, AttributeError):
        raise ValueError("A valid signed-in Supabase user ID is required.")


def ensure_initial_credits(user_id, starting_credits=None):
    """
    Gives a user their one-time Phase 1 starting credits.

    Safe to call on every login because transaction_key is unique.
    Returns the current credit balance.
    """
    user_id = _valid_user_id(user_id)
    amount = (
        DEFAULT_STARTING_CREDITS
        if starting_credits is None
        else int(starting_credits)
    )

    if amount <= 0:
        raise ValueError("Starting credits must be greater than zero.")

    transaction_key = f"initial-grant:{user_id}"
    client = _client()

    existing = (
        client
        .table("credit_transactions")
        .select("id")
        .eq("transaction_key", transaction_key)
        .limit(1)
        .execute()
    )

    if not existing.data:
        try:
            (
                client
                .table("credit_transactions")
                .insert({
                    "user_id": user_id,
                    "amount": amount,
                    "transaction_type": "initial_grant",
                    "description": "Phase 1 starting credits",
                    "transaction_key": transaction_key,
                })
                .execute()
            )
        except Exception:
            # If two requests race, the unique transaction_key lets only one win.
            # Re-read the balance instead of granting twice.
            pass

    return get_credit_balance(user_id)


def get_credit_balance(user_id):
    user_id = _valid_user_id(user_id)

    result = (
        _client()
        .rpc(
            "get_credit_balance",
            {"p_user_id": user_id},
        )
        .execute()
    )

    return int(result.data or 0)


def grant_credits(
    user_id,
    amount,
    description="Credit adjustment",
    transaction_type="admin_adjustment",
    transaction_key=None,
):
    """
    Backend/admin helper for Phase 1 testing.

    Later, Stripe/Apple/Google verified payment events will call the same
    ledger pattern instead of changing balances directly.
    """
    user_id = _valid_user_id(user_id)
    amount = int(amount)

    if amount <= 0:
        raise ValueError("Grant amount must be greater than zero.")

    allowed_types = {
        "initial_grant",
        "monthly_grant",
        "purchase",
        "refund",
        "admin_adjustment",
    }
    if transaction_type not in allowed_types:
        raise ValueError("Invalid credit transaction type.")

    payload = {
        "user_id": user_id,
        "amount": amount,
        "transaction_type": transaction_type,
        "description": description or "Credit adjustment",
    }

    if transaction_key:
        payload["transaction_key"] = transaction_key

    (
        _client()
        .table("credit_transactions")
        .insert(payload)
        .execute()
    )

    return get_credit_balance(user_id)


def spend_credits(
    user_id,
    amount,
    description="Channel Coach usage",
    transaction_key=None,
):
    """
    Atomically deduct credits. Returns the new balance.

    Raise RuntimeError with a friendly message if there are not enough credits.
    """
    user_id = _valid_user_id(user_id)
    amount = int(amount)

    if amount <= 0:
        raise ValueError("Spend amount must be greater than zero.")

    try:
        result = (
            _client()
            .rpc(
                "spend_credits",
                {
                    "p_user_id": user_id,
                    "p_amount": amount,
                    "p_description": description or "Channel Coach usage",
                    "p_transaction_key": transaction_key,
                },
            )
            .execute()
        )
    except Exception as exc:
        message = str(exc)
        if "Insufficient credits" in message:
            raise RuntimeError(
                "You do not have enough Channel Coach credits for that action."
            ) from exc
        raise

    return int(result.data or 0)


def credit_balance_html(user_id):
    """
    Small UI helper. Safe for a signed-out/invalid workspace.
    """
    try:
        balance = ensure_initial_credits(user_id)
        return (
            '<div class="cc-credit-balance">'
            '<span class="cc-credit-label">CREDITS</span>'
            f'<strong>{balance:,}</strong>'
            '</div>'
        )
    except Exception:
        return (
            '<div class="cc-credit-balance">'
            '<span class="cc-credit-label">CREDITS</span>'
            '<strong>—</strong>'
            '</div>'
        )

