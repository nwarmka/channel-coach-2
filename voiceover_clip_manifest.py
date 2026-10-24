"""Read-only ZIP export manifest validation for future Shotcut MP3 bundles.

No audio is generated, downloaded or exported here. The future authenticated
export handler must verify job ownership and fetch bytes from private storage.
"""
import re
import uuid

SAFE_MP3_NAME = re.compile(r"^section_[0-9]{3}\.mp3$")


def build_clip_manifest(clips):
    """Produce ordered, collision-free filenames from verified completed jobs."""
    if not isinstance(clips, list) or not 1 <= len(clips) <= 100:
        raise ValueError("Select between 1 and 100 completed clips.")
    seen_jobs = set()
    manifest = []
    for index, clip in enumerate(clips, start=1):
        if not isinstance(clip, dict) or clip.get("status") != "completed":
            raise ValueError("Every clip must be completed.")
        try:
            job_id = str(uuid.UUID(str(clip.get("id"))))
        except (TypeError, ValueError, AttributeError) as exc:
            raise ValueError("Invalid clip job ID.") from exc
        if job_id in seen_jobs:
            raise ValueError("Duplicate clip job ID.")
        seen_jobs.add(job_id)
        manifest.append({
            "job_id": job_id,
            "filename": f"section_{index:03d}.mp3",
            "order": index,
        })
    return manifest
