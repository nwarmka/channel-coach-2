"""Tests for deterministic, safe voiceover MP3 export manifests."""
import unittest
from voiceover_clip_manifest import build_clip_manifest

A = "7b0e3ac0-ffea-4bc8-8d83-1e6c1fd94bd1"
B = "57b52dd7-0c86-41a5-97fd-51c9a38f4a10"


class ClipManifestTests(unittest.TestCase):
    def test_ordered_clip_names_for_shotcut(self):
        manifest = build_clip_manifest([
            {"id": B, "status": "completed"},
            {"id": A, "status": "completed"},
        ])
        self.assertEqual([item["filename"] for item in manifest],
                         ["section_001.mp3", "section_002.mp3"])
        self.assertEqual([item["job_id"] for item in manifest], [B, A])

    def test_incomplete_clip_rejected(self):
        with self.assertRaises(ValueError):
            build_clip_manifest([{"id": A, "status": "processing"}])

    def test_duplicate_clip_rejected(self):
        with self.assertRaises(ValueError):
            build_clip_manifest([
                {"id": A, "status": "completed"},
                {"id": A, "status": "completed"},
            ])

    def test_invalid_job_id_rejected(self):
        with self.assertRaises(ValueError):
            build_clip_manifest([{"id": "../other.mp3", "status": "completed"}])

    def test_empty_manifest_rejected(self):
        with self.assertRaises(ValueError):
            build_clip_manifest([])

    def test_more_than_100_clips_rejected(self):
        with self.assertRaises(ValueError):
            build_clip_manifest([{"id": A, "status": "completed"}] * 101)


if __name__ == "__main__":
    unittest.main()
