"""Static integration checks for draft Script Studio app navigation.

These checks avoid importing app.py, which starts the production server.
"""
from pathlib import Path
import ast
import unittest


class VoiceoverAppNavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = Path("app.py").read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)

    def test_studio_builder_is_imported(self):
        self.assertIn("from ui.voiceover import build_voiceover_page", self.source)

    def test_studio_page_is_constructed(self):
        self.assertIn("voiceover_page = build_voiceover_page(saved_login, visible=False)",
                      self.source)

    def test_navigation_button_and_handler(self):
        self.assertIn('voiceover_nav = gr.Button("🎙️ Script Studio")', self.source)
        self.assertIn('voiceover_nav.click(', self.source)
        self.assertIn('navigate_to("voiceover", current)', self.source)

    def test_page_order_matches_navigation_order(self):
        names = [node.value for node in ast.walk(self.tree)
                 if isinstance(node, ast.Assign)
                 for target in node.targets
                 if isinstance(target, ast.Name) and target.id == "PAGE_NAMES"]
        self.assertEqual(len(names), 1)
        pages = ast.literal_eval(names[0])
        self.assertEqual(pages.index("voiceover"), pages.index("toolkit") + 1)
        self.assertRegex(self.source, r"toolkit_page,\s+voiceover_page,\s+settings_page,")


if __name__ == "__main__":
    unittest.main()
