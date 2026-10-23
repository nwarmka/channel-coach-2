"""Offline tests for private download plans."""
import unittest
from voiceover_download_plan import plan_private_clip_download

USER = "7b0e3ac0-ffea-4bc8-8d83-1e6c1fd94bd1"
OTHER = "57b52dd7-0c86-41a5-97fd-51c9a38f4a10"
JOB = "97e7855d-bd88-4998-9b7c-4d74e10c9758"


def record():
    return {"id": JOB, "user_id": USER, "status": "completed",
            "storage_path": f"{USER}/{JOB}.mp3"}


class DownloadPlanTests(unittest.TestCase):
    def test_private_bucket_and_short_lifetime(self):
        plan = plan_private_clip_download(USER, record())
        self.assertEqual(plan["bucket"], "voiceover-clips")
        self.assertEqual(plan["expires_in"], 60)
        self.assertEqual(plan["object_path"], f"{USER}/{JOB}.mp3")

    def test_cross_user_is_denied(self):
        with self.assertRaises(PermissionError):
            plan_private_clip_download(OTHER, record())

    def test_expiration_limit(self):
        for ttl in (0, 61, True, "60"):
            with self.subTest(ttl=ttl):
                with self.assertRaises(ValueError):
                    plan_private_clip_download(USER, record(), ttl)

    def test_incomplete_clip_denied(self):
        job = record()
        job["status"] = "processing"
        with self.assertRaises(ValueError):
            plan_private_clip_download(USER, job)


if __name__ == "__main__":
    unittest.main()
