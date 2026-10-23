"""Safe read-only preflight for a future atomic voiceover reservation.

This never charges credits or creates a job. It verifies that a quote, request
intent and available balance are internally consistent before any DB RPC.
The database transaction MUST revalidate everything under concurrency.
"""
from voiceover_job_intent import build_job_intent
from voiceover_quote import quote_is_current


class InsufficientVoiceoverCredits(ValueError):
    """The displayed balance is lower than the proposed cost."""


def preview_reservation(user_id, request_key, section_id, text, voice_id,
                        approved_snapshot, available_credits):
    if type(available_credits) is not int or available_credits < 0:
        raise ValueError("A valid nonnegative credit balance is required.")
    if not quote_is_current(approved_snapshot, section_id, text, voice_id):
        raise ValueError("The quote changed. Request a fresh quote.")
    intent = build_job_intent(user_id, request_key, section_id, text, voice_id)
    if intent["quoted_credits"] > available_credits:
        raise InsufficientVoiceoverCredits(
            "You do not have enough Channel Coach credits for this voiceover."
        )
    return {
        "intent": intent,
        "available_credits": available_credits,
        "remaining_if_approved": available_credits - intent["quoted_credits"],
        "charged": False,
        "generation_enabled": False,
    }
