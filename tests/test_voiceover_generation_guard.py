"""Fail-closed tests: no environment toggle can activate billing or generation."""
import os
import unittest
from unittest.mock import patch

from voiceover_generation_guard import (
    VoiceoverUnavailable,
    validate_generation_request,
)

USER = "7b0e3ac0-ffea-4bc8-8d83-1e6c1fd94bd1"


class VoiceoverGenerationGuardTests(unittest.TestCase):
    def test_generation_blocked_by_default(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(VoiceoverUnavailable):
                validate_generation_request(USER, "x" * 1000, "voice-1", 3)

    def test_environment_toggle_cannot_enable_generation(self):
        with patch.dict(os.environ, {"CHANNEL_COACH_VOICEOVER_GENERATION_ENABLED": "true"}):
            with self.assertRaises(VoiceoverUnavailable):
                validate_generation_request(USER, "x" * 1000, "voice-1", 3)

    def test_rejects_invalid_user(self):
        with self.assertRaises(ValueError):
            validate_generation_request("not-a-user", "Hello", "voice-1", 1)

    def test_rejects_missing_voice(self):
        with self.assertRaises(ValueError):
            validate_generation_request(USER, "Hello", "", 1)

    def test_rejects_mismatched_quote(self):
        with self.assertRaises(ValueError):
            validate_generation_request(USER, "x" * 1000, "voice-1", 2)

    def test_rejects_boolean_approved_credits(self):
        with self.assertRaises(ValueError):
            validate_generation_request(USER, "Hello", "voice-1", True)


if __name__ == "__main__":
    unittest.main()
