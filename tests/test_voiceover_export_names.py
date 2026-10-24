"""Tests for portable script export filenames."""
import unittest
from voiceover_export_names import safe_script_export_name


class ExportNamesTests(unittest.TestCase):
    def test_normal_title(self):
        self.assertEqual(safe_script_export_name("My Video!"), "My_Video.txt")

    def test_windows_reserved_name(self):
        self.assertEqual(safe_script_export_name("CON"), "script_CON.txt")

    def test_path_traversal_is_sanitized(self):
        result = safe_script_export_name("../../private\\secret")
        self.assertNotIn("/", result)
        self.assertNotIn("\\", result)

    def test_unicode_fallback(self):
        self.assertEqual(safe_script_export_name("🌟"), "voiceover_script.txt")

    def test_json_extension(self):
        self.assertEqual(safe_script_export_name("Script", ".json"), "Script.json")

    def test_invalid_extension(self):
        with self.assertRaises(ValueError):
            safe_script_export_name("Script", ".exe")


if __name__ == "__main__":
    unittest.main()
