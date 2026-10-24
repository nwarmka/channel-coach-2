"""Smoke-test real Gradio 6 construction, without credentials or network calls."""
import sys
import types
import unittest
from unittest.mock import patch


class VoiceoverGradioSmokeTests(unittest.TestCase):
    def test_builds_editor_and_authenticated_controls(self):
        import gradio as gr
        fake_inbox = types.ModuleType("ui.ideas_inbox")
        fake_inbox._authenticated_client = lambda session: (_ for _ in ()).throw(
            ValueError("Authentication disabled in smoke test")
        )
        with patch.dict(sys.modules, {"ui.ideas_inbox": fake_inbox}):
            from ui.voiceover import build_voiceover_page
            with gr.Blocks() as demo:
                build_voiceover_page(gr.State(None), visible=False)
        labels = [getattr(component, "label", None) for component in demo.blocks.values()]
        for expected in ("Your script", "Edit selected section", "Project title",
                         "Saved projects", "Import JSON script", "Download script"):
            self.assertIn(expected, labels)
        self.assertGreater(len(demo.fns), 15)


if __name__ == "__main__":
    unittest.main()
