"""Pure, non-billable quote snapshot regression tests."""
import unittest

from voiceover_quote import create_quote_snapshot, quote_is_current


class QuoteSnapshotTests(unittest.TestCase):
    def test_matching_snapshot(self):
        snapshot = create_quote_snapshot("0", "Hello world", "voice-a")
        self.assertEqual(snapshot["credits"], 1)
        self.assertTrue(quote_is_current(snapshot, "0", "Hello world", "voice-a"))

    def test_edit_invalidates_quote(self):
        snapshot = create_quote_snapshot("0", "Hello world", "voice-a")
        self.assertFalse(quote_is_current(snapshot, "0", "Hello world!", "voice-a"))

    def test_voice_change_invalidates_quote(self):
        snapshot = create_quote_snapshot("0", "Hello world", "voice-a")
        self.assertFalse(quote_is_current(snapshot, "0", "Hello world", "voice-b"))

    def test_section_change_invalidates_quote(self):
        snapshot = create_quote_snapshot("0", "Hello world", "voice-a")
        self.assertFalse(quote_is_current(snapshot, "1", "Hello world", "voice-a"))

    def test_tampered_price_invalidates_quote(self):
        snapshot = create_quote_snapshot("0", "Hello world", "voice-a")
        snapshot["credits"] = 0
        self.assertFalse(quote_is_current(snapshot, "0", "Hello world", "voice-a"))

    def test_missing_snapshot_is_invalid(self):
        self.assertFalse(quote_is_current(None, "0", "Hello", "voice-a"))

    def test_missing_voice_rejected(self):
        with self.assertRaises(ValueError):
            create_quote_snapshot("0", "Hello", "")


if __name__ == "__main__":
    unittest.main()
