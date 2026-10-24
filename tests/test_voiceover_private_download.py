"""Tests for strict private voiceover clip access validation."""
import unittest
from voiceover_private_download import validate_private_clip_request

USER = "7b0e3ac0-ffea-4bc8-8d83-1e6c1fd94bd1"
OTHER = "57b52dd7-0c86-41a5-97fd-51c9a38f4a10"
JOB = "97e7855d-bd88-4998-9b7c-4d74e10c9758"


def record(**changes):
    value = {
        "id": JOB, "user_id": USER, "status": "completed",
        "storage_path": f"{USER}/{JOB}.mp3",
    }
    value.update(changes)
    return value


class PrivateDownloadTests(unittest.TestCase):
    def test_valid_completed_owned_clip(self):
        self.assertEqual(validate_private_clip_request(USER, record()),
                         f"{USER}/{JOB}.mp3")

    def test_other_user_cannot_download(self):
        with self.assertRaises(PermissionError):
            validate_private_clip_request(OTHER, record())

    def test_processing_clip_is_not_downloadable(self):
        with self.assertRaises(ValueError):
            validate_private_clip_request(USER, record(status="processing"))

    def test_noncanonical_path_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_private_clip_request(USER, record(storage_path="../private.mp3"))

    def test_wrong_user_in_record_is_rejected(self):
        with self.assertRaises(PermissionError):
            validate_private_clip_request(USER, record(user_id=OTHER))

    def test_invalid_identity_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_private_clip_request("not-uuid", record())


if __name__ == "__main__":
    unittest.main()
