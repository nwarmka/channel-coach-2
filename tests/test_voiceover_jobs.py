"""Unit tests for voiceover job history access and input validation."""
import unittest
from unittest.mock import MagicMock

from voiceover_jobs import list_voiceover_jobs


USER_ID = "7b0e3ac0-ffea-4bc8-8d83-1e6c1fd94bd1"


class VoiceoverJobHistoryTests(unittest.TestCase):
    def test_rejects_missing_authentication(self):
        with self.assertRaises(ValueError):
            list_voiceover_jobs(None, USER_ID)

    def test_rejects_invalid_user(self):
        with self.assertRaises(ValueError):
            list_voiceover_jobs(MagicMock(), "not-a-uuid")

    def test_rejects_invalid_limit(self):
        for limit in (0, 101, True, "10"):
            with self.subTest(limit=limit):
                with self.assertRaises(ValueError):
                    list_voiceover_jobs(MagicMock(), USER_ID, limit)

    def test_scopes_query_to_verified_user_and_safe_columns(self):
        client = MagicMock()
        query = client.table.return_value
        query.select.return_value = query
        query.eq.return_value = query
        query.order.return_value = query
        query.limit.return_value = query
        query.execute.return_value.data = [
            {"id": "job-1", "status": "completed", "characters": 1000,
             "quoted_credits": 3, "created_at": "2026-10-23T12:00:00Z",
             "updated_at": "2026-10-23T12:01:00Z", "storage_path": "private-path"}
        ]
        result = list_voiceover_jobs(client, USER_ID, limit=5)
        client.table.assert_called_once_with("voiceover_generation_jobs")
        query.eq.assert_called_once_with("user_id", USER_ID)
        query.select.assert_called_once_with(
            "id,status,characters,quoted_credits,created_at,updated_at"
        )
        query.limit.assert_called_once_with(5)
        self.assertEqual(len(result), 1)
        self.assertNotIn("storage_path", result[0])


if __name__ == "__main__":
    unittest.main()
