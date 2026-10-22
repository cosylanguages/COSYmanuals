-- Behavioral assertions for docs/security-remediation-proposal.sql.
-- Run only against the disposable PostgreSQL service in GitHub Actions.
DO $$
DECLARE
  v_note public.lesson_notes%rowtype;
  v_result jsonb;
  v_id uuid;
BEGIN
  PERFORM set_config('request.jwt.claim.sub', '', false);
  BEGIN
    PERFORM * FROM public.join_lesson_note('0123456789abcdef0123456789abcdef', 'lesson-a');
    RAISE EXCEPTION 'FAIL: unauthenticated join unexpectedly succeeded';
  EXCEPTION WHEN SQLSTATE '28000' THEN NULL;
  END;
  IF EXISTS (SELECT 1 FROM public.lesson_notes WHERE lesson_id = 'lesson-a') THEN
    RAISE EXCEPTION 'FAIL: unauthenticated join created a row';
  END IF;

  PERFORM set_config('request.jwt.claim.sub', '00000000-0000-0000-0000-00000000000a', false);
  BEGIN
    PERFORM * FROM public.join_lesson_note('bad-key', 'lesson-a');
    RAISE EXCEPTION 'FAIL: malformed key unexpectedly succeeded';
  EXCEPTION WHEN SQLSTATE '22023' THEN NULL;
  END;

  SELECT * INTO v_note FROM public.join_lesson_note('0123456789abcdef0123456789abcdef', 'lesson-a');
  IF v_note.version <> 0 OR NOT ('00000000-0000-0000-0000-00000000000a'::uuid = ANY(v_note.participants)) THEN
    RAISE EXCEPTION 'FAIL: first join version/participant invariant';
  END IF;
  v_id := v_note.id;

  SELECT * INTO v_note FROM public.join_lesson_note('0123456789abcdef0123456789abcdef', 'lesson-a');
  IF cardinality(v_note.participants) <> 1 OR v_note.id <> v_id THEN
    RAISE EXCEPTION 'FAIL: repeat join duplicated participant or note';
  END IF;

  UPDATE public.lesson_notes SET content = 'seed', version = 4 WHERE id = v_id;
  PERFORM set_config('request.jwt.claim.sub', '00000000-0000-0000-0000-00000000000b', false);
  SELECT * INTO v_note FROM public.join_lesson_note('0123456789abcdef0123456789abcdef', 'lesson-a');
  IF cardinality(v_note.participants) <> 2 OR v_note.content <> 'seed' OR v_note.version <> 4 THEN
    RAISE EXCEPTION 'FAIL: second join changed content/version or omitted participant';
  END IF;

  PERFORM set_config('request.jwt.claim.sub', '00000000-0000-0000-0000-00000000000c', false);
  BEGIN
    PERFORM public.save_lesson_note(v_id, 'unauthorized overwrite', 4);
    RAISE EXCEPTION 'FAIL: unauthorized save unexpectedly succeeded';
  EXCEPTION WHEN SQLSTATE '42501' THEN NULL;
  END;
  IF (SELECT content FROM public.lesson_notes WHERE id = v_id) <> 'seed'
     OR (SELECT version FROM public.lesson_notes WHERE id = v_id) <> 4 THEN
    RAISE EXCEPTION 'FAIL: unauthorized save changed persisted row';
  END IF;

  PERFORM set_config('request.jwt.claim.sub', '00000000-0000-0000-0000-00000000000a', false);
  v_result := public.save_lesson_note(v_id, 'participant save', 4);
  IF (v_result->>'success')::boolean IS DISTINCT FROM true
     OR (v_result->>'version')::integer <> 5 THEN
    RAISE EXCEPTION 'FAIL: participant save did not increment version';
  END IF;
  v_result := public.save_lesson_note(v_id, 'stale overwrite', 4);
  IF (v_result->>'conflict')::boolean IS DISTINCT FROM true
     OR (v_result->>'version')::integer <> 5
     OR (SELECT content FROM public.lesson_notes WHERE id = v_id) <> 'participant save' THEN
    RAISE EXCEPTION 'FAIL: stale save did not conflict safely';
  END IF;

  PERFORM set_config('request.jwt.claim.sub', '00000000-0000-0000-0000-00000000000f', false);
  v_result := public.save_lesson_note(v_id, 'founder save', 5);
  IF (v_result->>'success')::boolean IS DISTINCT FROM true THEN
    RAISE EXCEPTION 'FAIL: founder RPC behavior changed';
  END IF;

  IF has_function_privilege('anon', 'public.join_lesson_note(text,text)', 'EXECUTE')
     OR has_function_privilege('anon', 'public.save_lesson_note(uuid,text,integer)', 'EXECUTE')
     OR NOT has_function_privilege('authenticated', 'public.join_lesson_note(text,text)', 'EXECUTE')
     OR NOT has_function_privilege('authenticated', 'public.save_lesson_note(uuid,text,integer)', 'EXECUTE') THEN
    RAISE EXCEPTION 'FAIL: RPC EXECUTE grant matrix';
  END IF;
  IF has_table_privilege('anon', 'public.manual_content', 'TRUNCATE')
     OR has_table_privilege('authenticated', 'public.manual_content', 'TRUNCATE')
     OR has_table_privilege('anon', 'public.lesson_content', 'REFERENCES')
     OR has_table_privilege('authenticated', 'public.lesson_content', 'TRIGGER')
     OR has_table_privilege('anon', 'public.student_lesson_content', 'MAINTAIN')
     OR has_table_privilege('authenticated', 'public.student_lesson_content', 'MAINTAIN') THEN
    RAISE EXCEPTION 'FAIL: dangerous content-table privilege remains';
  END IF;
  IF NOT has_table_privilege('service_role', 'public.manual_content', 'INSERT') THEN
    RAISE EXCEPTION 'FAIL: service-role publisher insert privilege was unexpectedly removed';
  END IF;
  IF NOT (SELECT relrowsecurity FROM pg_class WHERE oid='public.lesson_notes'::regclass)
     OR (SELECT count(*) FROM pg_policies WHERE schemaname='public' AND tablename='lesson_notes') <> 3 THEN
    RAISE EXCEPTION 'FAIL: lesson_notes RLS/policy baseline changed';
  END IF;
END $$;

CREATE TABLE public.security_future_table_postgres (id integer);
CREATE SEQUENCE public.security_future_sequence_postgres;
CREATE FUNCTION public.security_future_function_postgres() RETURNS integer LANGUAGE sql AS $$ SELECT 1 $$;
DO $$
BEGIN
  IF has_table_privilege('anon', 'public.security_future_table_postgres', 'SELECT')
     OR has_table_privilege('authenticated', 'public.security_future_table_postgres', 'SELECT')
     OR has_sequence_privilege('anon', 'public.security_future_sequence_postgres', 'USAGE')
     OR has_sequence_privilege('authenticated', 'public.security_future_sequence_postgres', 'USAGE')
     OR has_function_privilege('anon', 'public.security_future_function_postgres()', 'EXECUTE')
     OR has_function_privilege('authenticated', 'public.security_future_function_postgres()', 'EXECUTE') THEN
    RAISE EXCEPTION 'FAIL: postgres default ACLs still grant client access to new objects';
  END IF;
END $$;

SET ROLE supabase_admin;
CREATE TABLE public.security_future_table_admin (id integer);
CREATE SEQUENCE public.security_future_sequence_admin;
CREATE FUNCTION public.security_future_function_admin() RETURNS integer LANGUAGE sql AS $$ SELECT 1 $$;
RESET ROLE;
DO $$
BEGIN
  IF has_table_privilege('anon', 'public.security_future_table_admin', 'SELECT')
     OR has_table_privilege('authenticated', 'public.security_future_table_admin', 'SELECT')
     OR has_sequence_privilege('anon', 'public.security_future_sequence_admin', 'USAGE')
     OR has_sequence_privilege('authenticated', 'public.security_future_sequence_admin', 'USAGE')
     OR has_function_privilege('anon', 'public.security_future_function_admin()', 'EXECUTE')
     OR has_function_privilege('authenticated', 'public.security_future_function_admin()', 'EXECUTE') THEN
    RAISE EXCEPTION 'FAIL: supabase_admin default ACLs still grant client access to new objects';
  END IF;
END $$;

DROP TABLE public.security_future_table_postgres, public.security_future_table_admin;
DROP SEQUENCE public.security_future_sequence_postgres, public.security_future_sequence_admin;
DROP FUNCTION public.security_future_function_postgres(), public.security_future_function_admin();
