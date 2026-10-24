"""Tests for authenticated and RLS-scoped private clip lookup."""
import unittest
from unittest.mock import MagicMock
from voiceover_owned_job_lookup import get_owned_completed_voiceover_job

USER = "7b0e3ac0-ffea-4bc8-8d83-1e6c1fd94bd1"
OTHER = "57b52dd7-0c86-41a5-97fd-51c9a38f4a10"
JOB = "97e7855d-bd88-4998-9b7c-4d74e10c9758"


def client_with(rows):
    client = MagicMock()
    client.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.limit.return_value.execute.return_value.data = rows
    return client


class OwnedJobLookupTests(unittest.TestCase):
    def test_completed_job_query_scopes_user_and_status(self):
        row = {"id": JOB, "user_id": USER, "status": "completed",
               "storage_path": f"{USER}/{JOB}.mp3"}
        client = client_with([row])
        self.assertEqual(get_owned_completed_voiceover_job(client, USER, JOB), row)
        query = client.table.return_value.select.return_value
        query.eq.assert_any_call("id", JOB)
        query.eq.return_value.eq.assert_any_call("user_id", USER)
        query.eq.return_value.eq.return_value.eq.assert_any_call("status", "completed")

    def test_empty_query_is_not_found(self):
        with self.assertRaises(FileNotFoundError):
            get_owned_completed_voiceover_job(client_with([]), USER, JOB)

    def test_cross_user_record_denied_even_if_backend_returns_it(self):
        row = {"id": JOB, "user_id": OTHER, "status": "completed",
               "storage_path": f"{OTHER}/{JOB}.mp3"}
        with self.assertRaises(PermissionError):
            get_owned_completed_voiceover_job(client_with([row]), USER, JOB)

    def test_invalid_job_id_denied_before_query(self):
        client = client_with([])
        with self.assertRaises(ValueError):
            get_owned_completed_voiceover_job(client, USER, "../bad")
        client.table.assert_not_called()

    def test_incorrect_storage_path_denied(self):
        row = {"id": JOB, "user_id": USER, "status": "completed",
               "storage_path": f"{OTHER}/{JOB}.mp3"}
        with self.assertRaises(ValueError):
            get_owned_completed_voiceover_job(client_with([row]), USER, JOB)


if __name__ == "__main__":
    unittest.main()
