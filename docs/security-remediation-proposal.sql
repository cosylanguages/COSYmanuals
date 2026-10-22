-- PROPOSAL ONLY — DO NOT APPLY DIRECTLY TO PRODUCTION.
-- Prepared 2026-10-22 from a read-only audit of the connected Supabase project.
-- Canonical client review: COSYplatform-source/classroom.html and
-- supabase/migrations/0009_lesson_notes.sql.
--
-- The client generates a separate 32-hex-character bearer room key and calls
-- join_lesson_note after a browser-side PeerJS handshake. That handshake is NOT a
-- database authorization boundary. This proposal preserves the current signed-in
-- bearer-key join contract, validates the key format, and checks auth.uid().
-- Anyone who obtains the room key can join; confirm that this is the intended product
-- contract, and review key leakage, logging, rotation/expiry, and rate limiting.
--
-- This file is a review draft only. It has not been parsed/applied against staging.
-- Grant changes below are intentionally conservative/incomplete pending a full grant
-- inventory, owner/default-privilege review, and testing of legitimate publisher flows.

begin;

create or replace function public.join_lesson_note(room_key text, lesson_id text)
returns setof public.lesson_notes
language plpgsql
security definer
set search_path = ''
as $function$
declare
  caller_id uuid := auth.uid();
  note_rec public.lesson_notes%rowtype;
begin
  if caller_id is null then
    raise exception 'Authentication required' using errcode = '28000';
  end if;

  -- classroom.html generates a 32-character hexadecimal bearer room key.
  -- Treat it as a secret capability: anyone who knows it can join that room.
  if room_key is null or room_key !~ '^[0-9a-fA-F]{32}$'
     or lesson_id is null or btrim(lesson_id) = ''
     or length(lesson_id) > 512 then
    raise exception 'Invalid room or lesson' using errcode = '22023';
  end if;

  -- Preserve the intended join flow: a caller presenting the room key is added
  -- as a participant. The random room key is the authorization capability; the
  -- browser-side PeerJS handshake is not a database security boundary.
  insert into public.lesson_notes
    (room_key, lesson_id, content, version, participants, created_by, updated_by)
  values
    (room_key, lesson_id, '', 0, array[caller_id], caller_id, caller_id)
  on conflict on constraint lesson_notes_room_lesson_key do update
    set participants = case
          when caller_id = any(coalesce(lesson_notes.participants, array[]::uuid[]))
            then coalesce(lesson_notes.participants, array[]::uuid[])
          else array_append(coalesce(lesson_notes.participants, array[]::uuid[]), caller_id)
        end,
        updated_at = now()
  returning * into note_rec;

  return next note_rec;
end;
$function$;

create or replace function public.save_lesson_note(
  note_id uuid,
  content text,
  base_version integer
)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $function$
declare
  caller_id uuid := auth.uid();
  current_rec public.lesson_notes%rowtype;
begin
  if caller_id is null then
    raise exception 'Authentication required' using errcode = '28000';
  end if;

  if note_id is null or base_version is null or base_version < 0 then
    raise exception 'Invalid note or version' using errcode = '22023';
  end if;

  select ln.* into current_rec
  from public.lesson_notes as ln
  where ln.id = save_lesson_note.note_id
    and (caller_id = any(ln.participants) or public.is_founder())
  for update;

  if not found then
    -- Match the existing RPC/client contract: the caller handles RPC errors by
    -- retaining a local copy. Returning conflict=false here would be misread by
    -- classroom.html as a successful save with missing version/content fields.
    raise exception 'Note not found or access denied' using errcode = '42501';
  end if;

  -- Match the client contract: data.version and data.content are consumed by
  -- classroom.html; any version mismatch is a conflict, including stale/ahead bases.
  if coalesce(current_rec.version, 0) <> base_version then
    return jsonb_build_object('success', false, 'conflict', true,
                              'version', coalesce(current_rec.version, 0),
                              'content', current_rec.content);
  end if;

  update public.lesson_notes as ln
     set content = save_lesson_note.content,
         version = coalesce(current_rec.version, 0) + 1,
         updated_at = now(),
         updated_by = caller_id
   where ln.id = current_rec.id
   returning * into current_rec;

  return jsonb_build_object('success', true, 'conflict', false,
                            'version', current_rec.version,
                            'content', current_rec.content);
end;
$function$;

-- Keep execution grants explicit. Confirm client call paths before applying.
revoke all on function public.join_lesson_note(text, text) from public, anon;
grant execute on function public.join_lesson_note(text, text) to authenticated;

revoke all on function public.save_lesson_note(uuid, text, integer) from public, anon;
grant execute on function public.save_lesson_note(uuid, text, integer) to authenticated;

-- Remove dangerous table-level privileges only. Do not replace existing SELECT/INSERT/
-- UPDATE/DELETE grants until authoring and publishing requirements have been verified.
revoke truncate, references, trigger, maintain
  on table public.manual_content, public.lesson_content, public.student_lesson_content
  from public, anon, authenticated;

-- The live read-only inventory found broad default table, sequence, and function ACLs
-- for postgres and supabase_admin in public, including client-role grants. Default ACLs
-- are per object-creator role, so addressing postgres alone is incomplete. This fail-closed
-- proposal removes future implicit client grants; migrations must explicitly GRANT only
-- the table/sequence privileges and function EXECUTE permissions each client flow requires.
-- Review role membership/ownership and test every app path in staging before deployment.
alter default privileges for role postgres in schema public
  revoke all on tables from public, anon, authenticated;

alter default privileges for role supabase_admin in schema public
  revoke all on tables from public, anon, authenticated;

-- The same read-only catalog inventory shows client grants on future sequences
-- and functions. Without addressing these object types, a future SECURITY DEFINER
-- RPC may inherit EXECUTE for client roles, and client roles may inherit sequence
-- privileges. Treat this as a fail-closed default: grant only what each migration
-- actually requires and test all application paths in staging.
alter default privileges for role postgres in schema public
  revoke all on sequences from public, anon, authenticated;

alter default privileges for role supabase_admin in schema public
  revoke all on sequences from public, anon, authenticated;

alter default privileges for role postgres in schema public
  revoke execute on functions from public, anon, authenticated;

alter default privileges for role supabase_admin in schema public
  revoke execute on functions from public, anon, authenticated;

commit;

-- POST-APPLY VERIFICATION QUERIES (run only in staging):
-- 1) Assert anon/authenticated have no TRUNCATE/REFERENCES/TRIGGER/MAINTAIN on content tables.
-- 2) Assert existing manual_content entitlement policies are unchanged.
-- 3) Assert the two RPCs have search_path = '' and only intended EXECUTE grants.
-- 4) Verify default ACLs for every object-creator role (live inventory includes postgres
--    and supabase_admin); verify future tables receive no implicit client ACLs.
-- 5) Explicitly grant the minimum required table privileges to intended roles for each
--    future table; test Data API access and RLS/entitlement behavior.
-- 6) Run functional tests for each supported enrollment, authoring, publishing, and note flow.
--
-- IMPORTANT: This proposal is not yet merge-ready:
-- * join_lesson_note preserves self-join based on a 32-hex bearer key. Confirm that this
--   remains the intended authorization model; browser-side PeerJS checks are not sufficient.
-- * REVOKE from PUBLIC affects all roles that inherit PUBLIC grants. Check current grants.
-- * The default-privilege revokes remove future implicit client grants, including SELECT.
--   Future migrations must add explicit minimal grants; otherwise client access may fail.
-- * Default privileges are per object-creator role; inventory any additional roles beyond
--   postgres and supabase_admin before approval.
-- * Use a backup/rollback plan and apply only through an approved staging migration.
