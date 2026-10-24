"""Release gate checks for Stage 1 Script Studio.

This is a source-level guard, not a replacement for live Gradio and Supabase tests.
"""
from pathlib import Path
import ast
import unittest


class StageOneReleaseChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = Path("app.py").read_text(encoding="utf-8")
        cls.ui = Path("ui/voiceover.py").read_text(encoding="utf-8")
        cls.ui_tree = ast.parse(cls.ui)

    def test_navigation_is_in_app(self):
        self.assertIn("from ui.voiceover import build_voiceover_page", self.app)
        self.assertIn('navigate_to("voiceover", current)', self.app)

    def test_preview_is_explicit(self):
        self.assertIn("**Preview release:**", self.ui)
        self.assertIn("Voice generation and credit charging are not active.", self.ui)

    def test_script_editor_and_export_controls_exist(self):
        for name in ("Split into sections", "Add section", "Delete selected section",
                     "Prepare script download", "Save as new project",
                     "Open selected saved project"):
            self.assertIn(name, self.ui)

    def test_no_voice_generation_call_in_ui(self):
        banned = {"generate_voiceover", "generate_speech", "charge_credits",
                  "deduct_credits", "reserve_credits"}
        called = {node.func.id for node in ast.walk(self.ui_tree)
                  if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
        self.assertFalse(called & banned)


if __name__ == "__main__":
    unittest.main()
