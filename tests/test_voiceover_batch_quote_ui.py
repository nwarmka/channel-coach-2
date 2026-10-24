"""Offline test of draft studio full-script quote handler."""
import ast
from pathlib import Path
import unittest
from voiceover_batch_quote import quote_script_sections


def load_handler():
    tree = ast.parse(Path("ui/voiceover.py").read_text(encoding="utf-8"))
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef)
             and n.name == "quote_full_script"]
    if len(nodes) != 1:
        raise AssertionError("Missing whole-script quote handler")
    namespace = {"quote_script_sections": quote_script_sections}
    exec(compile(ast.Module(body=nodes, type_ignores=[]),
                 "ui/voiceover.py", "exec"), namespace)
    return namespace["quote_full_script"]


class WholeScriptQuoteUITests(unittest.TestCase):
    def test_quote_shows_total_without_charging(self):
        message = load_handler()(["Hello", "World"])
        self.assertIn("6 credits", message)
        self.assertIn("10 characters", message)
        self.assertIn("No credits charged", message)

    def test_empty_script_fails_safely(self):
        self.assertIn("Cannot quote script", load_handler()([]))


if __name__ == "__main__":
    unittest.main()
