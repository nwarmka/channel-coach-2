"""Tests for private project deletion safeguards."""
import unittest
from unittest.mock import MagicMock
from voiceover_project_delete import delete_script_project

USER = "7b0e3ac0-ffea-4bc8-8d83-1e6c1fd94bd1"
PROJECT = "97e7855d-bd88-4998-9b7c-4d74e10c9758"


class ProjectDeleteTests(unittest.TestCase):
    def test_delete_scopes_project_and_user(self):
        client = MagicMock()
        client.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value.data = [{"id": PROJECT}]
        self.assertTrue(delete_script_project(client, USER, PROJECT))
        client.table.assert_called_once_with("voiceover_script_projects")
        client.table.return_value.delete.return_value.eq.assert_called_with("id", PROJECT)
        client.table.return_value.delete.return_value.eq.return_value.eq.assert_called_with("user_id", USER)

    def test_missing_project_is_not_reported_as_deleted(self):
        client = MagicMock()
        client.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
        with self.assertRaises(FileNotFoundError):
            delete_script_project(client, USER, PROJECT)

    def test_wrong_project_returned_is_rejected(self):
        client = MagicMock()
        client.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value.data = [{"id": USER}]
        with self.assertRaises(FileNotFoundError):
            delete_script_project(client, USER, PROJECT)

    def test_invalid_project_id_does_not_query(self):
        client = MagicMock()
        with self.assertRaises(ValueError):
            delete_script_project(client, USER, "bad")
        client.table.assert_not_called()


if __name__ == "__main__":
    unittest.main()
