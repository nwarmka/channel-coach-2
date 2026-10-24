"""Regression tests: failed project load must not erase a working draft."""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch
import sys
import types


def handler():
    tree = ast.parse(Path("ui/voiceover.py").read_text(encoding="utf-8"))
    fn = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
              and node.name == "open_saved_script_draft")
    ns = {"gr": SimpleNamespace(update=lambda **kwargs: {"unchanged": True, **kwargs})}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), "<project-loader>", "exec"), ns)
    return ns["open_saved_script_draft"]


class SavedProjectFailureTests(TestCase):
    def test_access_denied_preserves_editor(self):
        module = types.ModuleType("voiceover_project_store")
        module.load_script_project = lambda *args: (_ for _ in ()).throw(FileNotFoundError())
        with patch.dict(sys.modules, {"voiceover_project_store": module}):
            fn = handler()
            fn.__globals__["_authenticated_client"] = lambda session: (object(), "user", session)
            title, sections, selection, editor, message, session = fn("session", "id")
        for value in (title, sections, selection, editor):
            self.assertEqual(value["unchanged"], True)
        self.assertIn("unchanged", message)
        self.assertEqual(session, "session")

    def test_database_failure_preserves_editor(self):
        module = types.ModuleType("voiceover_project_store")
        module.load_script_project = lambda *args: (_ for _ in ()).throw(RuntimeError("offline"))
        with patch.dict(sys.modules, {"voiceover_project_store": module}):
            fn = handler()
            fn.__globals__["_authenticated_client"] = lambda session: (object(), "user", session)
            title, sections, selection, editor, message, _ = fn("session", "id")
        for value in (title, sections, selection, editor):
            self.assertEqual(value["unchanged"], True)
        self.assertIn("unchanged", message)
