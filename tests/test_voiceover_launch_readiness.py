"""Tests for advisory launch readiness; no automatic feature enabling."""
import unittest
from voiceover_launch_readiness import (
    REQUIRED_LAUNCH_CHECKS, assess_voiceover_launch_readiness,
)


class LaunchReadinessTests(unittest.TestCase):
    def test_missing_checks_block_readiness(self):
        result = assess_voiceover_launch_readiness()
        self.assertFalse(result["ready"])
        self.assertEqual(len(result["missing"]), len(REQUIRED_LAUNCH_CHECKS))
        self.assertFalse(result["generation_enabled"])

    def test_partial_checks_still_block(self):
        result = assess_voiceover_launch_readiness({
            "elevenlabs_commercial_rights_verified": True
        })
        self.assertFalse(result["ready"])
        self.assertIn("atomic_credit_reservation_deployed", result["missing"])

    def test_all_checks_still_do_not_enable_generation(self):
        result = assess_voiceover_launch_readiness({
            name: True for name in REQUIRED_LAUNCH_CHECKS
        })
        self.assertTrue(result["ready"])
        self.assertFalse(result["generation_enabled"])
        self.assertFalse(result["billing_enabled"])

    def test_truthy_strings_are_not_accepted(self):
        result = assess_voiceover_launch_readiness({
            name: "yes" for name in REQUIRED_LAUNCH_CHECKS
        })
        self.assertFalse(result["ready"])


if __name__ == "__main__":
    unittest.main()
