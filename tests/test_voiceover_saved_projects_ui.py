"""Static integration checks for authenticated saved script workflows."""
from pathlib import Path
import ast
import unittest


class SavedScriptUITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = Path("ui/voiceover.py").read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)

    def test_project_handlers_exist(self):
        names = {node.name for node in cls_functions(self.tree)}
        for name in ("save_new_script_draft", "refresh_saved_script_drafts",
                     "open_saved_script_draft"):
            self.assertIn(name, names)

    def test_saved_project_controls_require_login_state(self):
        self.assertIn("if saved_login is not None:", self.source)
        self.assertIn("save_project_button.click(", self.source)
        self.assertIn("refresh_projects_button.click(", self.source)
        self.assertIn("open_project_button.click(", self.source)

    def test_save_is_insert_only(self):
        fn = next(n for n in cls_functions(self.tree)
                  if n.name == "save_new_script_draft")
        calls = [n for n in ast.walk(fn) if isinstance(n, ast.Call)]
        save_calls = [n for n in calls if isinstance(n.func, ast.Name)
                      and n.func.id == "save_script_project"]
        self.assertEqual(len(save_calls), 1)
        self.assertEqual(len(save_calls[0].args), 4)
        self.assertFalse(save_calls[0].keywords)


def cls_functions(tree):
    return [n for n in tree.body if isinstance(n, ast.FunctionDef)]


if __name__ == "__main__":
    unittest.main()
