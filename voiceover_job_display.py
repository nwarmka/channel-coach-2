"""Read-only voiceover job status normalization for safe UI rendering.

Never exposes storage keys, user IDs, or raw provider errors.
"""
from datetime import datetime, timezone

DISPLAY_STATUSES = {
    "pending": "Waiting",
    "reserved": "Credits reserved",
    "processing": "Generating",
    "completed": "Ready",
    "failed": "Failed",
    "review_required": "Needs review",
}


def summarize_voiceover_job(job):
    if not isinstance(job, dict):
        raise ValueError("Invalid voiceover job.")
    status = job.get("status")
    if status not in DISPLAY_STATUSES:
        raise ValueError("Unknown voiceover job status.")
    characters = job.get("characters")
    credits = job.get("quoted_credits")
    if type(characters) is not int or not 1 <= characters <= 5000:
        raise ValueError("Invalid character count.")
    if type(credits) is not int or credits < 1:
        raise ValueError("Invalid credit quote.")
    return {
        "job_id": str(job["id"]),
        "status": DISPLAY_STATUSES[status],
        "characters": characters,
        "quoted_credits": credits,
        "created_at": str(job.get("created_at") or ""),
    }


def summarize_voiceover_jobs(jobs):
    if not isinstance(jobs, list):
        raise ValueError("Invalid job history.")
    return [summarize_voiceover_job(job) for job in jobs]
