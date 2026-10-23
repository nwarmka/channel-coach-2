"""Offline ZIP packaging tests; no Supabase or ElevenLabs calls."""
from io import BytesIO
import unittest
from zipfile import ZipFile

from voiceover_zip import package_voiceover_mp3s

A = "7b0e3ac0-ffea-4bc8-8d83-1e6c1fd94bd1"
B = "57b52dd7-0c86-41a5-97fd-51c9a38f4a10"
MP3 = b"ID3" + b"fake-audio-for-unit-test"


class VoiceoverZipTests(unittest.TestCase):
    def test_archive_contains_ordered_mp3_files(self):
        archive = package_voiceover_mp3s([
            {"id": B, "status": "completed", "audio_bytes": MP3},
            {"id": A, "status": "completed", "audio_bytes": MP3},
        ])
        with ZipFile(BytesIO(archive)) as z:
            self.assertEqual(z.namelist(), ["section_001.mp3", "section_002.mp3"])
            self.assertEqual(z.read("section_001.mp3"), MP3)

    def test_reject_non_mp3_bytes(self):
        with self.assertRaises(ValueError):
            package_voiceover_mp3s([
                {"id": A, "status": "completed", "audio_bytes": b"not audio"},
            ])

    def test_reject_unfinished_job(self):
        with self.assertRaises(ValueError):
            package_voiceover_mp3s([
                {"id": A, "status": "processing", "audio_bytes": MP3},
            ])

    def test_reject_duplicate_jobs(self):
        with self.assertRaises(ValueError):
            package_voiceover_mp3s([
                {"id": A, "status": "completed", "audio_bytes": MP3},
                {"id": A, "status": "completed", "audio_bytes": MP3},
            ])

    def test_reject_oversized_clip(self):
        with self.assertRaises(ValueError):
            package_voiceover_mp3s([
                {"id": A, "status": "completed",
                 "audio_bytes": b"ID3" + b"x" * (25 * 1024 * 1024)},
            ])


if __name__ == "__main__":
    unittest.main()
