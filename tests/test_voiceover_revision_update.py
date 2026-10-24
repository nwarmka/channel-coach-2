"""Tests for conflict-aware voiceover script update preparation."""
import unittest
from voiceover_draft_revision import script_draft_revision
from voiceover_revision_update import (
    prepare_script_revision_update, ScriptRevisionConflictError,
)


class RevisionUpdateTests(unittest.TestCase):
    def test_valid_edit_prepares_new_revision(self):
        old = script_draft_revision("Video", ["Intro"])
        update = prepare_script_revision_update(
            old, "Video", ["Intro"], "Video", ["Updated intro"]
        )
        self.assertEqual(update["previous_revision"], old)
        self.assertEqual(update["sections"], ["Updated intro"])
        self.assertNotEqual(update["next_revision"], old)

    def test_stale_edit_is_rejected(self):
        old = script_draft_revision("Video", ["Intro"])
        with self.assertRaises(ScriptRevisionConflictError):
            prepare_script_revision_update(
                old, "Video", ["Someone else's edit"], "Video", ["My edit"]
            )

    def test_invalid_new_sections_rejected(self):
        old = script_draft_revision("Video", ["Intro"])
        with self.assertRaises(ValueError):
            prepare_script_revision_update(
                old, "Video", ["Intro"], "Video", [""]
            )

    def test_invalid_new_title_rejected(self):
        old = script_draft_revision("Video", ["Intro"])
        with self.assertRaises(ValueError):
            prepare_script_revision_update(
                old, "Video", ["Intro"], "", ["New"]
            )


if __name__ == "__main__":
    unittest.main()
