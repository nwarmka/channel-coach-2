"""Offline tests for safe script section copy."""
import unittest
from voiceover_section_copy import section_copy_text


class SectionCopyTests(unittest.TestCase):
    def test_selected_section_text(self):
        self.assertEqual(section_copy_text(["Intro", "Outro"], 1), "Outro")

    def test_preserves_inner_line_breaks(self):
        self.assertEqual(section_copy_text(["Line one\nLine two"], 0),
                         "Line one\nLine two")

    def test_rejects_invalid_index(self):
        with self.assertRaises(ValueError):
            section_copy_text(["Intro"], -1)

    def test_rejects_empty_section(self):
        with self.assertRaises(ValueError):
            section_copy_text([" "], 0)


if __name__ == "__main__":
    unittest.main()
