"""Test JSON draft import without Gradio or a database."""
import ast
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest


def import_handler():
    tree = ast.parse(Path("ui/voiceover.py").read_text(encoding="utf-8"))
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
              and n.name == "restore_script_from_json")
    namespace = {"gr": SimpleNamespace(update=lambda **kw: kw)}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), "<import-handler>", "exec"),
         namespace)
    return namespace["restore_script_from_json"]


class JSONImportUITests(unittest.TestCase):
    def test_valid_export_roundtrip(self):
        from voiceover_script_drafts import serialize_script_draft
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "draft.json"
            path.write_text(serialize_script_draft("My video", ["Intro", "Outro"]),
                            encoding="utf-8")
            title, sections, dropdown, editor, status = import_handler()(str(path))
        self.assertEqual(title, "My video")
        self.assertEqual(sections, ["Intro", "Outro"])
        self.assertEqual(dropdown["value"], "0")
        self.assertEqual(editor, "Intro")
        self.assertIn("imported", status)

    def test_reject_invalid_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "draft.json"
            path.write_text("not-json", encoding="utf-8")
            _, sections, _, _, status = import_handler()(str(path))
        self.assertEqual(sections, [])
        self.assertIn("Could not import", status)

    def test_reject_non_json_extension(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "draft.txt"
            path.write_text("hello", encoding="utf-8")
            _, sections, _, _, status = import_handler()(str(path))
        self.assertEqual(sections, [])
        self.assertIn("Could not import", status)

    def test_reject_oversized_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "draft.json"
            path.write_text("x" * 1_000_001, encoding="utf-8")
            _, sections, _, _, status = import_handler()(str(path))
        self.assertEqual(sections, [])
        self.assertIn("Could not import", status)


if __name__ == "__main__":
    unittest.main()
