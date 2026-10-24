"""Tests for stable idempotency keys and immutable generation inputs."""
import unittest
from voiceover_job_intent import build_job_intent, intent_matches_existing

USER = "7b0e3ac0-ffea-4bc8-8d83-1e6c1fd94bd1"
REQUEST = "57b52dd7-0c86-41a5-97fd-51c9a38f4a10"


class JobIntentTests(unittest.TestCase):
    def test_identical_retry_matches(self):
        original = build_job_intent(USER, REQUEST, "0", "Hello", "voice-a")
        retry = build_job_intent(USER, REQUEST, "0", "Hello", "voice-a")
        self.assertTrue(intent_matches_existing(retry, original))

    def test_different_text_is_not_same_job(self):
        original = build_job_intent(USER, REQUEST, "0", "Hello", "voice-a")
        changed = build_job_intent(USER, REQUEST, "0", "Hello!", "voice-a")
        self.assertFalse(intent_matches_existing(changed, original))

    def test_different_voice_is_not_same_job(self):
        original = build_job_intent(USER, REQUEST, "0", "Hello", "voice-a")
        changed = build_job_intent(USER, REQUEST, "0", "Hello", "voice-b")
        self.assertFalse(intent_matches_existing(changed, original))

    def test_different_user_is_not_same_job(self):
        original = build_job_intent(USER, REQUEST, "0", "Hello", "voice-a")
        changed = build_job_intent("fdc035d4-0874-4a36-ae44-cb7349d639a5",
                                   REQUEST, "0", "Hello", "voice-a")
        self.assertFalse(intent_matches_existing(changed, original))

    def test_reject_invalid_request_key(self):
        with self.assertRaises(ValueError):
            build_job_intent(USER, "bad-key", "0", "Hello", "voice-a")


if __name__ == "__main__":
    unittest.main()
