"""Exercise add/remove section callbacks without loading the production app."""
import ast
from pathlib import Path
import unittest
from types import SimpleNamespace


gr = SimpleNamespace(update=lambda **kwargs: kwargs)
from voiceover_section_editor import append_script_section, remove_script_section


def load_callback(name):
    tree = ast.parse(Path("ui/voiceover.py").read_text(encoding="utf-8"))
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    module = ast.Module(body=[node], type_ignores=[])
    namespace = {"gr": gr}
    exec(compile(module, "<studio-callback>", "exec"), namespace)
    return namespace[name]


class SectionEditingUITests(unittest.TestCase):
    def test_add_section(self):
        fn = load_callback("add_script_section")
        sections, _, text, status = fn(["Intro"])
        self.assertEqual(sections, ["Intro", "New section"])
        self.assertEqual(text, "New section")
        self.assertIn("added", status)

    def test_delete_section(self):
        fn = load_callback("delete_script_section")
        sections, _, text, status = fn("0", ["Intro", "Outro"])
        self.assertEqual(sections, ["Outro"])
        self.assertEqual(text, "Outro")
        self.assertIn("deleted", status)

    def test_cannot_delete_last_section(self):
        fn = load_callback("delete_script_section")
        sections, _, text, status = fn("0", ["Intro"])
        self.assertEqual(sections, ["Intro"])
        self.assertIn("Cannot delete", status)


if __name__ == "__main__":
    unittest.main()
