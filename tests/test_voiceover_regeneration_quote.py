"""Tests for individual clip regeneration quotes."""
import unittest
from voiceover_regeneration_quote import quote_clip_regeneration


class RegenerationQuoteTests(unittest.TestCase):
    def test_only_selected_section_is_quoted(self):
        quote = quote_clip_regeneration(["Hello", "World!"], 1)
        self.assertEqual(quote["characters"], 6)
        self.assertEqual(quote["credits"], 1)
        self.assertTrue(quote["requires_new_approval"])
        self.assertFalse(quote["generation_enabled"])

    def test_previous_job_does_not_remove_approval(self):
        quote = quote_clip_regeneration(["Hello"], 0, "previous")
        self.assertEqual(quote["previous_job_id"], "previous")
        self.assertTrue(quote["requires_new_approval"])

    def test_invalid_index_rejected(self):
        with self.assertRaises(ValueError):
            quote_clip_regeneration(["Hello"], 2)

    def test_boolean_index_rejected(self):
        with self.assertRaises(ValueError):
            quote_clip_regeneration(["Hello"], True)


if __name__ == "__main__":
    unittest.main()
