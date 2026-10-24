"""Offline tests for voiceover script TXT and JSON exports."""
import json
import unittest
from voiceover_script_export import build_script_export


class ScriptExportTests(unittest.TestCase):
    def test_txt_preserves_section_order(self):
        export = build_script_export("Video", ["Intro", "Outro"])
        self.assertEqual(export["filename"], "Video.txt")
        self.assertEqual(export["content"].decode(), "Intro\n\nOutro\n")

    def test_json_roundtrip(self):
        export = build_script_export("My Video", ["Hola 🌟"], "json")
        payload = json.loads(export["content"])
        self.assertEqual(payload["sections"], ["Hola 🌟"])
        self.assertEqual(payload["schema_version"], 1)

    def test_reject_invalid_format(self):
        with self.assertRaises(ValueError):
            build_script_export("Video", ["Intro"], "html")

    def test_reject_empty_section(self):
        with self.assertRaises(ValueError):
            build_script_export("Video", [""])

    def test_filename_is_safe(self):
        export = build_script_export("../../Video", ["Intro"])
        self.assertNotIn("/", export["filename"])


if __name__ == "__main__":
    unittest.main()
