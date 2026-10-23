"""Tests for read-only voiceover pricing. Run: python -m unittest tests.test_voiceover_pricing"""
import unittest

from voiceover_pricing import quote_voiceover_credits


class VoiceoverPricingTests(unittest.TestCase):
    def test_rounding(self):
        cases = [(1, 1), (500, 2), (1000, 3), (1001, 4), (2000, 6), (5000, 15)]
        for characters, expected in cases:
            with self.subTest(characters=characters):
                quote = quote_voiceover_credits("x" * characters)
                self.assertEqual(quote["credits"], expected)
                self.assertEqual(quote["characters"], characters)

    def test_reject_empty_or_oversized(self):
        for text in ("", "   ", "x" * 5001):
            with self.assertRaises(ValueError):
                quote_voiceover_credits(text)

    def test_reject_other_model(self):
        with self.assertRaises(ValueError):
            quote_voiceover_credits("hello", model_id="other-model")

    def test_no_external_side_effects(self):
        self.assertEqual(quote_voiceover_credits("hello")["rate_per_1000_characters"], 3)


if __name__ == "__main__":
    unittest.main()
