"""Voiceover UI history tests run with a stub Gradio module, no database."""
import sys
import types
import unittest
from unittest.mock import patch, MagicMock

try:
    import gradio
except ImportError:
    sys.modules["gradio"] = types.ModuleType("gradio")

from ui.voiceover import refresh_voiceover_history


class VoiceoverHistoryUITests(unittest.TestCase):
    def test_signed_out_user_gets_no_rows(self):
        with patch("ui.voiceover._authenticated_client", side_effect=ValueError("expired")):
            rows, status, session = refresh_voiceover_history({})
        self.assertEqual(rows, [])
        self.assertIn("Sign in", status)
        self.assertEqual(session, {})

    def test_only_safe_columns_are_rendered(self):
        session = {"access_token": "test"}
        with patch("ui.voiceover._authenticated_client",
                   return_value=(MagicMock(), "user", session)):
            with patch("ui.voiceover.list_voiceover_jobs", return_value=[{
                "id": "job-1", "status": "completed", "characters": 100,
                "quoted_credits": 1, "created_at": "2026-10-23T12:00:00Z",
                "storage_path": "private/audio.mp3",
            }]):
                rows, status, updated = refresh_voiceover_history(session)
        self.assertEqual(rows, [["2026-10-23T12:00:00", "Ready", 100, 1]])
        self.assertNotIn("private/audio.mp3", repr(rows))
        self.assertEqual(updated, session)

    def test_missing_database_table_is_nonfatal(self):
        with patch("ui.voiceover._authenticated_client",
                   return_value=(MagicMock(), "user", {})):
            with patch("ui.voiceover.list_voiceover_jobs",
                       side_effect=RuntimeError("relation does not exist")):
                rows, status, _ = refresh_voiceover_history({})
        self.assertEqual(rows, [])
        self.assertIn("not available", status)


if __name__ == "__main__":
    unittest.main()
