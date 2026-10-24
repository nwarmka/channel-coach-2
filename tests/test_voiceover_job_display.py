"""Tests for safe, read-only voiceover job history presentation."""
import unittest
from voiceover_job_display import summarize_voiceover_job, summarize_voiceover_jobs


class JobDisplayTests(unittest.TestCase):
    def test_private_fields_are_never_displayed(self):
        job = {
            "id": "job-1", "status": "completed", "characters": 1500,
            "quoted_credits": 5, "created_at": "2026-10-23T12:00:00Z",
            "storage_path": "secret/path.mp3", "user_id": "secret-user",
            "error_code": "provider-private-error",
        }
        result = summarize_voiceover_job(job)
        self.assertEqual(result["status"], "Ready")
        self.assertNotIn("storage_path", result)
        self.assertNotIn("user_id", result)
        self.assertNotIn("error_code", result)

    def test_review_required_is_not_reported_as_failed(self):
        result = summarize_voiceover_job({
            "id": "job-2", "status": "review_required",
            "characters": 1, "quoted_credits": 1,
        })
        self.assertEqual(result["status"], "Needs review")

    def test_reject_unknown_status(self):
        with self.assertRaises(ValueError):
            summarize_voiceover_job({
                "id": "job-3", "status": "refunded",
                "characters": 10, "quoted_credits": 1,
            })

    def test_reject_invalid_counts(self):
        for chars, credits in ((True, 1), (0, 1), (5001, 1), (1, 0), (1, True)):
            with self.subTest(chars=chars, credits=credits):
                with self.assertRaises(ValueError):
                    summarize_voiceover_job({
                        "id": "job-4", "status": "pending",
                        "characters": chars, "quoted_credits": credits,
                    })

    def test_empty_history(self):
        self.assertEqual(summarize_voiceover_jobs([]), [])


if __name__ == "__main__":
    unittest.main()
