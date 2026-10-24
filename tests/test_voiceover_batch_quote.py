"""Offline batch narration quote tests."""
import unittest
from voiceover_batch_quote import quote_script_sections


class BatchQuoteTests(unittest.TestCase):
    def test_all_sections_quoted_individually(self):
        quote = quote_script_sections(["Hi", "Bye"])
        self.assertEqual(quote["total_characters"], 5)
        self.assertEqual(quote["total_credits"], 6)
        self.assertEqual([row["index"] for row in quote["sections"]], [0, 1])

    def test_selected_section_only(self):
        quote = quote_script_sections(["Hi", "Bye"], [1])
        self.assertEqual(quote["total_credits"], 3)
        self.assertEqual(quote["sections"][0]["index"], 1)

    def test_duplicate_selection_rejected(self):
        with self.assertRaises(ValueError):
            quote_script_sections(["Hi"], [0, 0])

    def test_invalid_section_rejected(self):
        with self.assertRaises(ValueError):
            quote_script_sections(["Hi"], [1])

    def test_empty_selection_rejected(self):
        with self.assertRaises(ValueError):
            quote_script_sections(["Hi"], [])

    def test_boolean_index_rejected(self):
        with self.assertRaises(ValueError):
            quote_script_sections(["Hi"], [True])


if __name__ == "__main__":
    unittest.main()
