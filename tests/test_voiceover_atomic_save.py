"""Offline tests for atomic script project revision saves."""
import unittest
from unittest.mock import MagicMock
from voiceover_atomic_save import save_script_if_unchanged
from voiceover_draft_revision import script_draft_revision
from voiceover_revision_update import ScriptRevisionConflictError

USER = "7b0e3ac0-ffea-4bc8-8d83-1e6c1fd94bd1"
PROJECT = "97e7855d-bd88-4998-9b7c-4d74e10c9758"


class AtomicSaveTests(unittest.TestCase):
    def test_successful_compare_and_swap(self):
        client = MagicMock()
        client.rpc.return_value.execute.return_value.data = True
        old = script_draft_revision("Video", ["Intro"])
        revision = save_script_if_unchanged(
            client, USER, PROJECT, old, "Video", ["Intro"],
            "Video", ["Revised"]
        )
        self.assertNotEqual(revision, old)
        name, payload = client.rpc.call_args.args
        self.assertEqual(name, "update_voiceover_script_project_if_revision")
        self.assertEqual(payload["p_previous_revision"], old)
        self.assertEqual(payload["p_next_revision"], revision)

    def test_stale_script_never_calls_rpc(self):
        client = MagicMock()
        old = script_draft_revision("Video", ["Intro"])
        with self.assertRaises(ScriptRevisionConflictError):
            save_script_if_unchanged(
                client, USER, PROJECT, old, "Video", ["Other edit"],
                "Video", ["My edit"]
            )
        client.rpc.assert_not_called()

    def test_database_conflict_fails_closed(self):
        client = MagicMock()
        client.rpc.return_value.execute.return_value.data = False
        old = script_draft_revision("Video", ["Intro"])
        with self.assertRaises(RuntimeError):
            save_script_if_unchanged(
                client, USER, PROJECT, old, "Video", ["Intro"],
                "Video", ["New"]
            )

    def test_invalid_user_rejected_without_rpc(self):
        client = MagicMock()
        old = script_draft_revision("Video", ["Intro"])
        with self.assertRaises(ValueError):
            save_script_if_unchanged(
                client, "bad", PROJECT, old, "Video", ["Intro"],
                "Video", ["New"]
            )
        client.rpc.assert_not_called()


if __name__ == "__main__":
    unittest.main()
