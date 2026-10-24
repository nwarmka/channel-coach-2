"""Offline Gradio script export adapter tests without importing Gradio.

The draft page is not wired into the live app. These tests exercise the
handler extracted from source so CI does not need UI dependencies.
"""
import ast
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from voiceover_script_export import build_script_export


def load_export_handler():
    source = Path("ui/voiceover.py").read_text(encoding="utf-8")
    module = ast.parse(source)
    functions = [node for node in module.body
                 if isinstance(node, ast.FunctionDef)
                 and node.name == "export_script_file"]
    if len(functions) != 1:
        raise AssertionError("Expected exactly one script export handler")
    namespace = {"build_script_export": build_script_export}
    exec(compile(ast.Module(body=functions, type_ignores=[]),
                 "ui/voiceover.py", "exec"), namespace)
    return namespace["export_script_file"]


class ExportUITests(unittest.TestCase):
    def test_txt_export_creates_downloadable_file(self):
        handler = load_export_handler()
        with tempfile.TemporaryDirectory() as directory:
            with patch("tempfile.mkdtemp", return_value=directory):
                path, message = handler("My Video", ["Intro", "Outro"], "txt")
                self.assertEqual(Path(path).name, "My_Video.txt")
                self.assertEqual(Path(path).read_text(), "Intro\n\nOutro\n")
                self.assertIn("No credits charged", message)

    def test_invalid_script_returns_no_file(self):
        handler = load_export_handler()
        path, message = handler("Video", [""], "txt")
        self.assertIsNone(path)
        self.assertIn("Cannot export", message)

    def test_json_export_preserves_unicode(self):
        handler = load_export_handler()
        with tempfile.TemporaryDirectory() as directory:
            with patch("tempfile.mkdtemp", return_value=directory):
                path, _ = handler("Video", ["Hola 🌟"], "json")
                self.assertIn("Hola 🌟", Path(path).read_text())


if __name__ == "__main__":
    unittest.main()
