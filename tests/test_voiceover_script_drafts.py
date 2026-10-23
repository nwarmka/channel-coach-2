"""Offline tests for draft script serialization and section safety."""
import json
import unittest
from voiceover_script_drafts import (
    serialize_script_draft, deserialize_script_draft,
)


class ScriptDraftTests(unittest.TestCase):
    def test_unicode_roundtrip_preserves_section_order(self):
        data = serialize_script_draft("My video", ["  Hola 🌟 ", "Second scene"])
        self.assertEqual(deserialize_script_draft(data), {
            "schema_version": 1,
            "title": "My video",
            "sections": ["Hola 🌟", "Second scene"],
        })

    def test_reject_empty_project(self):
        with self.assertRaises(ValueError):
            serialize_script_draft("Title", [])

    def test_reject_oversized_section(self):
        with self.assertRaises(ValueError):
            serialize_script_draft("Title", ["x" * 5001])

    def test_reject_too_many_sections(self):
        with self.assertRaises(ValueError):
            serialize_script_draft("Title", ["x"] * 101)

    def test_reject_invalid_title(self):
        with self.assertRaises(ValueError):
            serialize_script_draft(" ", ["Hello"])

    def test_reject_unknown_schema(self):
        with self.assertRaises(ValueError):
            deserialize_script_draft(json.dumps({
                "schema_version": 2, "title": "Test", "sections": ["Hello"]
            }))

    def test_reject_malformed_json(self):
        with self.assertRaises(ValueError):
            deserialize_script_draft("{broken")


if __name__ == "__main__":
    unittest.main()
