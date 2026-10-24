"""Mocked tests for private script project persistence."""
import unittest
from unittest.mock import MagicMock
from voiceover_project_store import (
    save_script_project, list_script_projects, load_script_project,
)

USER = "7b0e3ac0-ffea-4bc8-8d83-1e6c1fd94bd1"
PROJECT = "97e7855d-bd88-4998-9b7c-4d74e10c9758"


class ProjectStoreTests(unittest.TestCase):
    def test_create_project_scopes_user(self):
        client = MagicMock()
        client.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": PROJECT}
        ]
        result = save_script_project(client, USER, "Video", ["Intro"])
        self.assertEqual(result, PROJECT)
        row = client.table.return_value.insert.call_args.args[0]
        self.assertEqual(row["user_id"], USER)
        self.assertEqual(row["sections"], ["Intro"])

    def test_update_rejected_without_database_call(self):
        client = MagicMock()
        with self.assertRaisesRegex(ValueError, "Save a new copy"):
            save_script_project(client, USER, "Video", ["Intro"], project_id=PROJECT)
        client.table.assert_not_called()

    def test_list_projects_filters_user(self):
        client = MagicMock()
        client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = []
        self.assertEqual(list_script_projects(client, USER), [])
        client.table.return_value.select.return_value.eq.assert_called_with("user_id", USER)

    def test_load_project_preserves_sections(self):
        client = MagicMock()
        client.table.return_value.select.return_value.eq.return_value.eq.return_value.limit.return_value.execute.return_value.data = [{
            "id": PROJECT, "title": "Video", "sections": ["First", "Second"],
            "schema_version": 1,
        }]
        result = load_script_project(client, USER, PROJECT)
        self.assertEqual(result["sections"], ["First", "Second"])

    def test_missing_project_raises(self):
        client = MagicMock()
        client.table.return_value.select.return_value.eq.return_value.eq.return_value.limit.return_value.execute.return_value.data = []
        with self.assertRaises(FileNotFoundError):
            load_script_project(client, USER, PROJECT)

    def test_invalid_project_id_rejected(self):
        client = MagicMock()
        with self.assertRaises(ValueError):
            load_script_project(client, USER, "../bad")
        client.table.assert_not_called()


if __name__ == "__main__":
    unittest.main()
