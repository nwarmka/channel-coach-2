"""Regression tests for read-only voiceover reservation preflight."""
import unittest

from voiceover_quote import create_quote_snapshot
from voiceover_reservation_preflight import (
    InsufficientVoiceoverCredits, preview_reservation,
)

USER = "7b0e3ac0-ffea-4bc8-8d83-1e6c1fd94bd1"
KEY = "57b52dd7-0c86-41a5-97fd-51c9a38f4a10"


def preview(text="Hello", balance=5, snapshot=None):
    if snapshot is None:
        snapshot = create_quote_snapshot("0", text, "voice-a")
    return preview_reservation(USER, KEY, "0", text, "voice-a", snapshot, balance)


class ReservationPreflightTests(unittest.TestCase):
    def test_quote_and_balance_preview_never_charges(self):
        result = preview()
        self.assertEqual(result["remaining_if_approved"], 4)
        self.assertFalse(result["charged"])
        self.assertFalse(result["generation_enabled"])

    def test_exact_balance_is_allowed(self):
        self.assertEqual(preview(balance=1)["remaining_if_approved"], 0)

    def test_insufficient_balance_is_rejected(self):
        with self.assertRaises(InsufficientVoiceoverCredits):
            preview(balance=0)

    def test_stale_quote_is_rejected(self):
        old = create_quote_snapshot("0", "Hello", "voice-a")
        with self.assertRaises(ValueError):
            preview(text="Hello again", snapshot=old)

    def test_invalid_balance_is_rejected(self):
        for balance in (-1, True, "100", None):
            with self.subTest(balance=balance):
                with self.assertRaises(ValueError):
                    preview(balance=balance)

    def test_invalid_request_key_is_rejected(self):
        snapshot = create_quote_snapshot("0", "Hello", "voice-a")
        with self.assertRaises(ValueError):
            preview_reservation(USER, "bad-key", "0", "Hello", "voice-a",
                                snapshot, 10)


if __name__ == "__main__":
    unittest.main()
