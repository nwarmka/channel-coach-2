"""ElevenLabs adapter tests use mocked HTTP and never make real API calls."""
import os
from pathlib import Path
import requests
import unittest
from unittest.mock import patch, MagicMock

from elevenlabs_service import ElevenLabsError, generate_speech, list_voices


class ElevenLabsServiceTests(unittest.TestCase):
    def test_missing_api_key_fails_closed(self):
        with patch.dict(os.environ, {"ELEVENLABS_API_KEY": ""}):
            with self.assertRaises(ElevenLabsError):
                list_voices()

    def test_voice_id_encoded_and_response_closed_on_error(self):
        response = MagicMock()
        response.raise_for_status.side_effect = requests.HTTPError("provider rejected")
        with patch.dict(os.environ, {"ELEVENLABS_API_KEY": "fake-key"}):
            with patch("elevenlabs_service.requests.post", return_value=response) as post:
                with self.assertRaises(ElevenLabsError):
                    generate_speech("Hello", "voice/unsafe")
                self.assertIn("voice%2Funsafe", post.call_args.args[0])
                response.close.assert_called_once()

    def test_non_mp3_response_rejected(self):
        response = MagicMock()
        response.headers = {"Content-Type": "application/json"}
        with patch.dict(os.environ, {"ELEVENLABS_API_KEY": "fake-key"}):
            with patch("elevenlabs_service.requests.post", return_value=response):
                with self.assertRaises(ElevenLabsError):
                    generate_speech("Hello", "voice-1")
        response.close.assert_called_once()

    def test_stream_failure_removes_partial_file(self):
        response = MagicMock()
        response.headers = {"Content-Type": "audio/mpeg"}
        response.iter_content.return_value = iter([b"partial", None])
        with patch.dict(os.environ, {"ELEVENLABS_API_KEY": "fake-key"}):
            with patch("elevenlabs_service.requests.post", return_value=response):
                with patch("elevenlabs_service.NamedTemporaryFile") as temp:
                    import tempfile
                    with tempfile.NamedTemporaryFile(delete=False) as file:
                        path = file.name
                    temp.return_value.__enter__.return_value.name = path
                    temp.return_value.__enter__.return_value.write.side_effect = RuntimeError("disk error")
                    with self.assertRaises(RuntimeError):
                        generate_speech("Hello", "voice-1")
                    self.assertFalse(Path(path).exists())
        response.close.assert_called_once()

    def test_reject_oversized_text_without_api_call(self):
        with patch("elevenlabs_service.requests.post") as post:
            with self.assertRaises(ValueError):
                generate_speech("x" * 5001, "voice-1")
            post.assert_not_called()

    def test_reject_missing_voice_without_api_call(self):
        with patch("elevenlabs_service.requests.post") as post:
            with self.assertRaises(ValueError):
                generate_speech("Hello", "")
            post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
