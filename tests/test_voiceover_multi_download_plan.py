"""Offline tests for owned multi-clip download manifests."""
import unittest
from voiceover_multi_download_plan import plan_multiple_clip_downloads

USER = "7b0e3ac0-ffea-4bc8-8d83-1e6c1fd94bd1"
OTHER = "57b52dd7-0c86-41a5-97fd-51c9a38f4a10"
JOBS = [
    "97e7855d-bd88-4998-9b7c-4d74e10c9758",
    "e69b6cc9-12ab-46e1-b6a4-b72b46850dc3",
]


def job(index):
    ident = JOBS[index]
    return {"id": ident, "user_id": USER, "status": "completed",
            "storage_path": f"{USER}/{ident}.mp3"}


class MultiDownloadPlanTests(unittest.TestCase):
    def test_ordered_files_and_private_bucket(self):
        plans = plan_multiple_clip_downloads(USER, [job(0), job(1)])
        self.assertEqual([p["download_filename"] for p in plans],
                         ["section_001.mp3", "section_002.mp3"])
        self.assertTrue(all(p["bucket"] == "voiceover-clips" for p in plans))

    def test_duplicate_job_rejected(self):
        with self.assertRaises(ValueError):
            plan_multiple_clip_downloads(USER, [job(0), job(0)])

    def test_cross_user_job_rejected(self):
        with self.assertRaises(PermissionError):
            plan_multiple_clip_downloads(OTHER, [job(0)])

    def test_unfinished_job_rejected(self):
        pending = job(0)
        pending["status"] = "pending"
        with self.assertRaises(ValueError):
            plan_multiple_clip_downloads(USER, [pending])

    def test_empty_selection_rejected(self):
        with self.assertRaises(ValueError):
            plan_multiple_clip_downloads(USER, [])


if __name__ == "__main__":
    unittest.main()
