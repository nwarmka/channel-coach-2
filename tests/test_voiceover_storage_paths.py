"""Private voiceover MP3 path validation regression tests."""
import unittest

from voiceover_storage_paths import voiceover_object_path, is_owned_voiceover_path

USER = "7b0e3ac0-ffea-4bc8-8d83-1e6c1fd94bd1"
OTHER = "fdc035d4-0874-4a36-ae44-cb7349d639a5"
JOB = "57b52dd7-0c86-41a5-97fd-51c9a38f4a10"


class VoiceoverStoragePathTests(unittest.TestCase):
    def test_canonical_mp3_path(self):
        self.assertEqual(voiceover_object_path(USER, JOB), f"{USER}/{JOB}.mp3")

    def test_owned_path(self):
        path = voiceover_object_path(USER, JOB)
        self.assertTrue(is_owned_voiceover_path(USER, JOB, path))

    def test_cross_user_path_rejected(self):
        path = voiceover_object_path(USER, JOB)
        self.assertFalse(is_owned_voiceover_path(OTHER, JOB, path))

    def test_prefix_and_traversal_not_accepted(self):
        path = voiceover_object_path(USER, JOB)
        for unsafe in (path + ".bak", path + "/../other.mp3", "/" + path,
                       path.replace(".mp3", ".wav"), None):
            with self.subTest(unsafe=unsafe):
                self.assertFalse(is_owned_voiceover_path(USER, JOB, unsafe))

    def test_invalid_uuid_rejected(self):
        with self.assertRaises(ValueError):
            voiceover_object_path(USER, "../other")


if __name__ == "__main__":
    unittest.main()
