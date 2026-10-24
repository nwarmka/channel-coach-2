"""Ensure character usage refreshes after edits complete, not concurrently."""
from pathlib import Path
import unittest


class UsageRefreshWiringTests(unittest.TestCase):
    def test_editor_operations_refresh_usage(self):
        source = Path("ui/voiceover.py").read_text(encoding="utf-8")
        self.assertIn(
            "selected.change(preview_section_usage, inputs=[selected, sections], outputs=[usage])",
            source,
        )
        for event, control in (
            ("save_event", "save.click"),
            ("add_event", "add_section.click"),
            ("delete_event", "delete_section.click"),
            ("up_event", "up.click"),
            ("down_event", "down.click"),
        ):
            self.assertIn(f"{event} = {control}(", source)
            self.assertNotIn(
                f"{control}(preview_section_usage, inputs=[selected, sections], outputs=[usage])",
                source,
                msg=f"{control} must not race the edit",
            )
        self.assertIn(
            "for edit_event in (save_event, add_event, delete_event, up_event, down_event):",
            source,
        )
        self.assertIn(
            "edit_event.then(preview_section_usage, inputs=[selected, sections], outputs=[usage])",
            source,
        )


if __name__ == "__main__":
    unittest.main()
