"""Verify UI script size limits without importing the full app."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest


def callback(name):
    tree = ast.parse(Path("ui/voiceover.py").read_text(encoding="utf-8"))
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    namespace = {"gr": SimpleNamespace(update=lambda **kwargs: kwargs),
                 "re": __import__("re")}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), "<callback>", "exec"),
         namespace)
    return namespace[name]


class ScriptSizeValidationTests(unittest.TestCase):
    def test_oversized_split_rejected(self):
        parts, _, _, status = callback("split_script")("x" * 5001)
        self.assertEqual(parts, [])
        self.assertIn("5,000", status)

    def test_exact_limit_allowed(self):
        parts, _, _, status = callback("split_script")("x" * 5000)
        self.assertEqual(len(parts), 1)
        self.assertIn("ready", status)

    def test_oversized_edit_does_not_mutate_sections(self):
        original = ["hello"]
        sections, _, status = callback("save_section")("0", "x" * 5001, original)
        self.assertEqual(sections, original)
        self.assertIn("5,000", status)

    def test_normal_edit_succeeds(self):
        sections, _, status = callback("save_section")("0", "Updated", ["hello"])
        self.assertEqual(sections, ["Updated"])
        self.assertIn("saved", status)


if __name__ == "__main__":
    unittest.main()
