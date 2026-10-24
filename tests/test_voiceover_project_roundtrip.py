"""Exercise save, list and reopen with a session-scoped fake Supabase client.

This does not replace a real authenticated integration test.
"""
import unittest
from types import SimpleNamespace
from voiceover_project_store import save_script_project, list_script_projects, load_script_project

USER_A = "7b0e3ac0-ffea-4bc8-8d83-1e6c1fd94bd1"
USER_B = "dbe5c12c-95aa-427d-8e7b-f40dd0344b77"
PROJECT = "97e7855d-bd88-4998-9b7c-4d74e10c9758"


class FakeClient:
    def __init__(self, session_user):
        self.session_user = session_user
        self.rows = []
        self.filters = []
        self.action = None
        self.payload = None

    def table(self, name):
        if name != "voiceover_script_projects":
            raise AssertionError("Unexpected table")
        self.filters = []
        return self

    def insert(self, row):
        self.action = "insert"
        self.payload = row
        return self

    def select(self, columns):
        self.action = "select"
        self.columns = columns.split(",")
        return self

    def eq(self, field, value):
        self.filters.append((field, value))
        return self

    def order(self, *args, **kwargs):
        return self

    def limit(self, count):
        return self

    def execute(self):
        if self.action == "insert":
            if self.payload["user_id"] != self.session_user:
                raise PermissionError("RLS rejected cross-user insert")
            row = dict(self.payload, id=PROJECT, updated_at="2026-10-23T00:00:00Z")
            self.rows.append(row)
            return SimpleNamespace(data=[row])
        matched = [row for row in self.rows if row["user_id"] == self.session_user
                   and all(row.get(field) == value for field, value in self.filters)]
        return SimpleNamespace(data=[
            {field: row[field] for field in self.columns} for row in matched
        ])


class RoundTripTests(unittest.TestCase):
    def test_save_list_reopen_and_isolate(self):
        client = FakeClient(USER_A)
        sections = ["Opening narration", "Second scene"]
        project_id = save_script_project(client, USER_A, "My video", sections)
        self.assertEqual(project_id, PROJECT)
        self.assertEqual([p["id"] for p in list_script_projects(client, USER_A)], [PROJECT])
        restored = load_script_project(client, USER_A, project_id)
        self.assertEqual(restored["title"], "My video")
        self.assertEqual(restored["sections"], sections)

        # The same storage must not expose A's project to B's session.
        client.session_user = USER_B
        self.assertEqual(list_script_projects(client, USER_B), [])
        with self.assertRaises(FileNotFoundError):
            load_script_project(client, USER_B, project_id)
        with self.assertRaises(PermissionError):
            save_script_project(client, USER_A, "Not mine", ["Text"])


if __name__ == "__main__":
    unittest.main()
