-- Draft schema for future authenticated, idempotent voiceover generation jobs.
-- REVIEW BEFORE APPLYING. This migration is not deployed by the PR.
-- Requires Supabase auth.users and pgcrypto (gen_random_uuid).
create table if not exists public.voiceover_generation_jobs (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    request_key uuid not null,
    section_sha256 text not null check (section_sha256 ~ '^[0-9a-f]{64}$'),
    voice_id text not null check (length(voice_id) between 1 and 128),
    model_id text not null default 'eleven_multilingual_v2',
    characters integer not null check (characters between 1 and 5000),
    quoted_credits integer not null check (quoted_credits > 0),
    status text not null default 'pending' check (
        status in ('pending','reserved','processing','completed','failed','review_required')
    ),
    storage_path text,
    error_code text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (user_id, request_key),
    check (storage_path is null or status = 'completed')
);

create index if not exists voiceover_jobs_user_created_idx
    on public.voiceover_generation_jobs (user_id, created_at desc);

alter table public.voiceover_generation_jobs enable row level security;

-- A user can read only their own job status; mutations must be server-side.
drop policy if exists voiceover_jobs_read_own on public.voiceover_generation_jobs;
create policy voiceover_jobs_read_own
    on public.voiceover_generation_jobs
    for select to authenticated
    using (user_id = (select auth.uid()));

revoke all on public.voiceover_generation_jobs from anon;
revoke insert, update, delete on public.voiceover_generation_jobs from authenticated;

-- Future worker design:
-- 1. Verify Supabase session server-side; never trust user_id supplied by client.
-- 2. Reserve a unique request_key and deduct credits atomically in ONE database
--    transaction; ledger transaction_key must be deterministic for this job.
-- 3. Persist a 'reserved' state before calling ElevenLabs. Handle retries by
--    reading the existing job, never issuing a second provider request blindly.
-- 4. Write MP3 into user-private storage, then mark completed.
-- 5. Reconcile failed/uncertain provider calls before any idempotent refund.
-- 6. A timeout does NOT prove provider failure; use review_required rather
--    than automatically retrying and charging again.
