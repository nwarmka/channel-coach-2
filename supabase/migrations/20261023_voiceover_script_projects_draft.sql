-- DRAFT ONLY: do not deploy without checking existing schema and RLS.
-- User-private script projects for AI Script & Voiceover Studio.
create table if not exists public.voiceover_script_projects (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    title text not null check (char_length(title) between 1 and 120),
    sections jsonb not null check (
        jsonb_typeof(sections) = 'array'
        and jsonb_array_length(sections) between 1 and 100
    ),
    schema_version integer not null default 1 check (schema_version = 1),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);
create index if not exists voiceover_script_projects_user_updated_idx
    on public.voiceover_script_projects(user_id, updated_at desc);
alter table public.voiceover_script_projects enable row level security;
drop policy if exists voiceover_script_projects_read_own on public.voiceover_script_projects;
create policy voiceover_script_projects_read_own
    on public.voiceover_script_projects for select to authenticated
    using (user_id = (select auth.uid()));
drop policy if exists voiceover_script_projects_insert_own on public.voiceover_script_projects;
create policy voiceover_script_projects_insert_own
    on public.voiceover_script_projects for insert to authenticated
    with check (user_id = (select auth.uid()));
-- Stage 1 is insert-only: do not permit editing or deleting cloud drafts yet.
-- Drop stale policies if this draft is ever re-applied to an existing table.
drop policy if exists voiceover_script_projects_update_own on public.voiceover_script_projects;
drop policy if exists voiceover_script_projects_delete_own on public.voiceover_script_projects;
revoke all on public.voiceover_script_projects from anon;
revoke update, delete on public.voiceover_script_projects from authenticated;
grant select, insert on public.voiceover_script_projects to authenticated;
-- The application must still enforce per-section length and total project size.
