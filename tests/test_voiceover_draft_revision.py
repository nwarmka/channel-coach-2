"""Offline tests for script revision conflicts."""
import unittest
from voiceover_draft_revision import script_draft_revision, draft_has_conflict


class DraftRevisionTests(unittest.TestCase):
    def test_unchanged_draft_has_no_conflict(self):
        revision = script_draft_revision("Video", ["Intro", "Outro"])
        self.assertFalse(draft_has_conflict(revision, "Video", ["Intro", "Outro"]))

    def test_reordering_changes_revision(self):
        revision = script_draft_revision("Video", ["Intro", "Outro"])
        self.assertTrue(draft_has_conflict(revision, "Video", ["Outro", "Intro"]))

    def test_title_change_detected(self):
        revision = script_draft_revision("Video", ["Intro"])
        self.assertTrue(draft_has_conflict(revision, "New title", ["Intro"]))

    def test_whitespace_is_canonicalized(self):
        self.assertEqual(script_draft_revision(" Video ", [" Intro "]),
                         script_draft_revision("Video", ["Intro"]))

    def test_invalid_revision_rejected(self):
        with self.assertRaises(ValueError):
            draft_has_conflict("not-a-revision", "Video", ["Intro"])


if __name__ == "__main__":
    unittest.main()
