"""Offline signed-download tests with mocked authenticated Supabase client."""
import unittest
from unittest.mock import MagicMock, patch
from voiceover_signed_download import create_private_clip_download_url

USER = "7b0e3ac0-ffea-4bc8-8d83-1e6c1fd94bd1"
JOB = "97e7855d-bd88-4998-9b7c-4d74e10c9758"


class SignedDownloadTests(unittest.TestCase):
    def test_private_bucket_and_60_second_link(self):
        client = MagicMock()
        client.storage.from_.return_value.create_signed_url.return_value = {
            "signedURL": "https://storage.example/clip?token=test"
        }
        row = {"id": JOB, "user_id": USER, "status": "completed",
               "storage_path": f"{USER}/{JOB}.mp3"}
        with patch("voiceover_signed_download.get_owned_completed_voiceover_job",
                   return_value=row):
            result = create_private_clip_download_url(client, USER, JOB)
        self.assertEqual(result["expires_in"], 60)
        self.assertEqual(result["url"], "https://storage.example/clip?token=test")
        client.storage.from_.assert_called_once_with("voiceover-clips")
        client.storage.from_.return_value.create_signed_url.assert_called_once_with(
            f"{USER}/{JOB}.mp3", 60
        )

    def test_missing_owned_job_never_calls_storage(self):
        client = MagicMock()
        with patch("voiceover_signed_download.get_owned_completed_voiceover_job",
                   side_effect=FileNotFoundError("missing")):
            with self.assertRaises(FileNotFoundError):
                create_private_clip_download_url(client, USER, JOB)
        client.storage.from_.assert_not_called()

    def test_insecure_or_missing_url_rejected(self):
        row = {"id": JOB, "user_id": USER, "status": "completed",
               "storage_path": f"{USER}/{JOB}.mp3"}
        for response in ({}, {"signedURL": "http://example.com/clip"}, None):
            client = MagicMock()
            client.storage.from_.return_value.create_signed_url.return_value = response
            with patch("voiceover_signed_download.get_owned_completed_voiceover_job",
                       return_value=row):
                with self.subTest(response=response):
                    with self.assertRaises(RuntimeError):
                        create_private_clip_download_url(client, USER, JOB)


if __name__ == "__main__":
    unittest.main()
