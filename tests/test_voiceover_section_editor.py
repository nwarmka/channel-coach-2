"""Tests for edit/reorder behavior before voiceover generation."""
import unittest
from voiceover_section_editor import (
    move_script_section, replace_script_section,
    append_script_section, remove_script_section,
)


class SectionEditorTests(unittest.TestCase):
    def test_move_forward_preserves_all_sections(self):
        original = ["Intro", "Middle", "Outro"]
        self.assertEqual(move_script_section(original, 0, 2),
                         ["Middle", "Outro", "Intro"])
        self.assertEqual(original, ["Intro", "Middle", "Outro"])

    def test_move_backward(self):
        self.assertEqual(move_script_section(["A", "B", "C"], 2, 0),
                         ["C", "A", "B"])

    def test_replace_one_section(self):
        self.assertEqual(replace_script_section(["A", "B"], 1, " New "),
                         ["A", "New"])

    def test_append_section(self):
        self.assertEqual(append_script_section(["A"], " B "), ["A", "B"])

    def test_remove_section(self):
        self.assertEqual(remove_script_section(["A", "B"], 0), ["B"])

    def test_cannot_remove_last_section(self):
        with self.assertRaises(ValueError):
            remove_script_section(["A"], 0)

    def test_invalid_index_rejected(self):
        for index in (-1, 2, True, "0"):
            with self.subTest(index=index):
                with self.assertRaises(ValueError):
                    move_script_section(["A", "B"], index, 0)

    def test_empty_edit_rejected(self):
        with self.assertRaises(ValueError):
            replace_script_section(["A"], 0, " ")

    def test_section_limit(self):
        with self.assertRaises(ValueError):
            append_script_section(["A"] * 100, "B")


if __name__ == "__main__":
    unittest.main()
