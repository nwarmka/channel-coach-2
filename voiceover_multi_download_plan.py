"""Create a safe manifest of clip-download requests.

Manifest planning only. Each item must be an owned, completed job verified by
the server; no audio is fetched or exposed by this helper.
"""
from voiceover_download_plan import plan_private_clip_download


def plan_multiple_clip_downloads(verified_user_id, verified_jobs):
    if not isinstance(verified_jobs, list) or not 1 <= len(verified_jobs) <= 100:
        raise ValueError("Select between 1 and 100 completed clips.")
    seen = set()
    plans = []
    for index, job in enumerate(verified_jobs, start=1):
        if not isinstance(job, dict) or job.get("id") is None:
            raise ValueError("Invalid clip record.")
        job_id = str(job["id"])
        if job_id in seen:
            raise ValueError("Duplicate clip.")
        seen.add(job_id)
        plan = plan_private_clip_download(verified_user_id, job)
        plan["download_filename"] = f"section_{index:03d}.mp3"
        plans.append(plan)
    return plans
