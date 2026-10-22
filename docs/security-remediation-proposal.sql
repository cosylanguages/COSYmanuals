-- PROPOSAL ONLY — DO NOT APPLY DIRECTLY TO PRODUCTION.
-- Prepared 2026-10-22 from a read-only audit of the connected Supabase project.
-- Review the room enrollment/product flow and test in an isolated staging database first.
--
-- This proposal intentionally does not create participants from knowledge of room_key.
-- The current join_lesson_note function creates a note and returns it to any caller who
-- supplies a room key. A secure replacement must use an established enrollment/invitation
-- mechanism. Until that mechanism is identified, this version permits existing participants
-- (and founders only if product requirements explicitly permit it) to retrieve an existing
-- note, and does not create new notes.

begin;

create or replace function public.join_lesson_note(room_key text, lesson_id text)
returns setof public.lesson_notes
language plpgsql
security definer
set search_path = ''
as $function$
declare
  caller_id uuid := auth.uid();
begin
  if caller_id is null then
    raise exception 'Authentication required' using errcode = '28000';
  end if;

  if room_key is null or btrim(room_key) = ''
     or lesson_id is null or btrim(lesson_id) = '' then
    raise exception 'Invalid room or lesson' using errcode = '22023';
  end if;

  -- Do not create a row or reveal whether a room exists to a non-participant.
  return query
    select ln.*
    from public.lesson_notes as ln
    where ln.room_key = join_lesson_note.room_key
      and ln.lesson_id = join_lesson_note.lesson_id
      and caller_id = any(ln.participants);

  if not found then
    raise exception 'Note not found or access denied' using errcode = '42501';
  end if;
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

  -- Lock only a row the caller is already authorized to access. The authorization
  -- check is inside this SECURITY DEFINER function; table RLS cannot protect it.
  select ln.* into current_rec
  from public.lesson_notes as ln
  where ln.id = save_lesson_note.note_id
    and caller_id = any(ln.participants)
  for update;

  if not found then
    -- Same response for nonexistent and unauthorized IDs to avoid existence leaks.
    return jsonb_build_object('success', false, 'error', 'Note not found or access denied');
  end if;

  if current_rec.version > base_version then
    return jsonb_build_object(
      'success', false,
      'conflict', true,
      'version', current_rec.version,
      'content', current_rec.content
    );
  end if;

  update public.lesson_notes as ln
     set content = save_lesson_note.content,
         version = current_rec.version + 1,
         updated_at = now(),
         updated_by = caller_id
   where ln.id = current_rec.id;

  return jsonb_build_object(
    'success', true,
    'conflict', false,
    'version', current_rec.version + 1,
    'content', save_lesson_note.content
  );
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

-- Stop future public-schema tables from inheriting client access. This applies only to
-- objects created by postgres; review all other object owners/default ACLs separately.
alter default privileges for role postgres in schema public
  revoke all on tables from public, anon, authenticated;

commit;

-- POST-APPLY VERIFICATION QUERIES (run only in staging):
-- 1) Assert anon/authenticated have no TRUNCATE/REFERENCES/TRIGGER/MAINTAIN on content tables.
-- 2) Assert existing manual_content entitlement policies are unchanged.
-- 3) Assert the two RPCs have search_path = '' and only intended EXECUTE grants.
-- 4) Verify default ACLs for every owner role, not only postgres.
-- 5) Run functional tests for each supported enrollment, authoring, publishing, and note flow.
--
-- IMPORTANT: This proposal is not yet merge-ready:
-- * join_lesson_note no longer self-creates rows. Confirm and implement a trusted room
--   creation/invitation/enrollment flow before deploying, or this can break valid clients.
-- * REVOKE from PUBLIC affects all roles that inherit PUBLIC grants. Check current grants.
-- * Default privileges must be set for every role that creates public tables.
-- * Use a backup/rollback plan and apply only through an approved staging migration.
