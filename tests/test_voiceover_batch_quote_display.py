"""Tests for narration batch credit breakdown formatting."""
import unittest
from voiceover_batch_quote_display import format_batch_quote


class BatchQuoteDisplayTests(unittest.TestCase):
    def test_full_breakdown(self):
        result = format_batch_quote(["Hi", "There"])
        self.assertIn("Total: 2 credits for 7 characters", result)
        self.assertIn("Section 1: 1 credits", result)
        self.assertIn("Section 2: 1 credits", result)
        self.assertIn("No credits charged", result)

    def test_selected_only(self):
        result = format_batch_quote(["Hi", "There"], [1])
        self.assertIn("Total: 1 credits", result)
        self.assertIn("Section 2:", result)
        self.assertNotIn("Section 1:", result)

    def test_invalid_script_fails_closed(self):
        with self.assertRaises(ValueError):
            format_batch_quote([])


if __name__ == "__main__":
    unittest.main()
