"""Isolated history-handler tests without loading the Gradio application."""
import ast
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock

source = Path(__file__).resolve().parents[1] / "ui" / "voiceover.py"
tree = ast.parse(source.read_text(encoding="utf-8"))
function = next(node for node in tree.body
                if isinstance(node, ast.FunctionDef)
                and node.name == "refresh_voiceover_history")
namespace = {}
exec(compile(ast.Module(body=[function], type_ignores=[]), str(source), "exec"), namespace)
refresh_voiceover_history = namespace["refresh_voiceover_history"]


class VoiceoverHistoryUITests(unittest.TestCase):
    def test_signed_out_user_gets_no_rows(self):
        with patch.dict(namespace, {
            "_authenticated_client": MagicMock(side_effect=ValueError("expired"))
        }):
            rows, status, session = refresh_voiceover_history({})
        self.assertEqual(rows, [])
        self.assertIn("Sign in", status)
        self.assertEqual(session, {})

    def test_only_safe_columns_are_rendered(self):
        session = {"access_token": "test"}
        from voiceover_job_display import summarize_voiceover_jobs
        with patch.dict(namespace, {
            "_authenticated_client": MagicMock(return_value=(MagicMock(), "user", session)),
            "list_voiceover_jobs": MagicMock(return_value=[{
                "id": "job-1", "status": "completed", "characters": 100,
                "quoted_credits": 1, "created_at": "2026-10-23T12:00:00Z",
                "storage_path": "private/audio.mp3",
            }]),
            "summarize_voiceover_jobs": summarize_voiceover_jobs,
        }):
            rows, status, updated = refresh_voiceover_history(session)
        self.assertEqual(rows, [["2026-10-23T12:00:00", "Ready", 100, 1]])
        self.assertNotIn("private/audio.mp3", repr(rows))
        self.assertEqual(updated, session)

    def test_missing_database_table_is_nonfatal(self):
        with patch.dict(namespace, {
            "_authenticated_client": MagicMock(return_value=(MagicMock(), "user", {})),
            "list_voiceover_jobs": MagicMock(side_effect=RuntimeError("relation missing")),
        }):
            rows, status, _ = refresh_voiceover_history({})
        self.assertEqual(rows, [])
        self.assertIn("not available", status)


if __name__ == "__main__":
    unittest.main()
