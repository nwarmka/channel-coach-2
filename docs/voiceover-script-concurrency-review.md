# Script project concurrency review checklist

This document covers the development-only script save/resume implementation.

## Before database deployment

- Review the existing `voiceover_script_projects` table and all migration ordering.
- Add a non-null revision for **new** projects; backfill existing projects using the same canonical serialization as `voiceover_draft_revision.py` before requiring non-null revisions.
- Ensure the server verifies the authenticated user and does not trust a browser-supplied user ID.
- Enforce section string type, per-section length, title length, and total payload size at a trusted boundary.
- Review RPC grants, RLS, and `security invoker` semantics on the target Supabase/Postgres version.
- Do not trust browser-computed `p_next_revision` as proof of payload integrity; recompute on the server or inside the database.
- Test concurrent updates with two separate database sessions: exactly one should succeed for the same previous revision.
- Test that one user cannot update, read, or delete another user's projects.
- Test that a missing project returns the same safe user-facing error as an unauthorized project.
- Review the draft project's ordinary `update` policy: it currently permits direct updates that bypass compare-and-swap. **Remove or restrict that path before claiming atomic conflict protection.**
- Never use a service-role client for user-facing project CRUD.

## Current limitations

The SQL and Python RPC helper are **not deployed or wired into the live UI**.
The Python helper's local conflict check is advisory; the SQL predicate is the
atomic enforcement point, but it requires migration, hardening, and integration.
