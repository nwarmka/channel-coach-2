-- DRAFT ONLY: additive schema and atomic compare-and-swap for script projects.
-- Review against the live schema before applying; not deployed.
alter table public.voiceover_script_projects
    add column if not exists revision text;

-- Existing rows are backfilled from canonical application JSON before making
-- revision NOT NULL. Do not deploy this migration before the backfill.
-- For new installations, the application must provide the revision.

create or replace function public.update_voiceover_script_project_if_revision(
    p_project_id uuid,
    p_previous_revision text,
    p_title text,
    p_sections jsonb,
    p_next_revision text
) returns boolean
language plpgsql
security invoker
set search_path = ''
as $$
declare
    updated_count integer;
begin
    if auth.uid() is null
       or p_previous_revision is null
       or p_previous_revision !~ '^[0-9a-f]{64}$'
       or p_next_revision is null
       or p_next_revision !~ '^[0-9a-f]{64}$'
       or p_title is null
       or char_length(btrim(p_title)) not between 1 and 120
       or p_sections is null
       or jsonb_typeof(p_sections) is distinct from 'array'
       or jsonb_array_length(p_sections) not between 1 and 100
    then
        raise exception 'Invalid script update request';
    end if;

    update public.voiceover_script_projects
    set title = btrim(p_title),
        sections = p_sections,
        revision = p_next_revision,
        updated_at = now()
    where id = p_project_id
      and user_id = (select auth.uid())
      and revision = p_previous_revision;

    get diagnostics updated_count = row_count;
    return updated_count = 1;
end;
$$;
revoke all on function public.update_voiceover_script_project_if_revision(
    uuid, text, text, jsonb, text
) from public, anon;
grant execute on function public.update_voiceover_script_project_if_revision(
    uuid, text, text, jsonb, text
) to authenticated;
-- The application must verify next_revision is the SHA256 of the canonical
-- payload; this SQL checks format only. For a production implementation,
-- enforce canonical content and revision in trusted server-side code.
