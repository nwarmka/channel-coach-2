"""Ensure character usage refreshes after every editor section operation."""
from pathlib import Path
import unittest


class UsageRefreshWiringTests(unittest.TestCase):
    def test_editor_operations_refresh_usage(self):
        source = Path("ui/voiceover.py").read_text(encoding="utf-8")
        for control in ("selected.change", "save.click", "add_section.click",
                        "delete_section.click", "up.click", "down.click"):
            self.assertIn(
                f"{control}(preview_section_usage, inputs=[selected, sections], outputs=[usage])",
                source,
                msg=f"Missing usage refresh after {control}",
            )


if __name__ == "__main__":
    unittest.main()
