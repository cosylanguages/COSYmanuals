-- TEST-ONLY inverse for the disposable PostgreSQL fixture.
-- This restores the known fixture baseline, NOT the unknown live Supabase ACL state.
DROP FUNCTION public.join_lesson_note(text, text);
DROP FUNCTION public.save_lesson_note(uuid, text, integer);

GRANT ALL ON public.manual_content, public.lesson_content, public.student_lesson_content
  TO anon, authenticated, service_role;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
  GRANT ALL ON TABLES TO anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
  GRANT ALL ON SEQUENCES TO anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
  GRANT EXECUTE ON FUNCTIONS TO anon, authenticated, service_role;

ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public
  GRANT ALL ON TABLES TO anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public
  GRANT ALL ON SEQUENCES TO anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public
  GRANT EXECUTE ON FUNCTIONS TO anon, authenticated, service_role;

-- Verify that the fixture's known pre-change privilege behavior is restored.
DO $$
BEGIN
  IF NOT has_table_privilege('anon', 'public.manual_content', 'TRUNCATE')
     OR NOT has_table_privilege('authenticated', 'public.lesson_content', 'REFERENCES')
     OR NOT has_table_privilege('anon', 'public.student_lesson_content', 'TRIGGER') THEN
    RAISE EXCEPTION 'FAIL: fixture table ACL baseline was not restored';
  END IF;
END $$;

CREATE TABLE public.security_rollback_table_postgres (id integer);
CREATE SEQUENCE public.security_rollback_sequence_postgres;
CREATE FUNCTION public.security_rollback_function_postgres() RETURNS integer LANGUAGE sql AS $$ SELECT 1 $$;
DO $$
BEGIN
  IF NOT has_table_privilege('anon', 'public.security_rollback_table_postgres', 'SELECT')
     OR NOT has_sequence_privilege('authenticated', 'public.security_rollback_sequence_postgres', 'USAGE')
     OR NOT has_function_privilege('anon', 'public.security_rollback_function_postgres()', 'EXECUTE') THEN
    RAISE EXCEPTION 'FAIL: postgres default ACL baseline was not restored';
  END IF;
END $$;

SET ROLE supabase_admin;
CREATE TABLE public.security_rollback_table_admin (id integer);
CREATE SEQUENCE public.security_rollback_sequence_admin;
CREATE FUNCTION public.security_rollback_function_admin() RETURNS integer LANGUAGE sql AS $$ SELECT 1 $$;
RESET ROLE;
DO $$
BEGIN
  IF NOT has_table_privilege('anon', 'public.security_rollback_table_admin', 'SELECT')
     OR NOT has_sequence_privilege('authenticated', 'public.security_rollback_sequence_admin', 'USAGE')
     OR NOT has_function_privilege('anon', 'public.security_rollback_function_admin()', 'EXECUTE') THEN
    RAISE EXCEPTION 'FAIL: supabase_admin default ACL baseline was not restored';
  END IF;
END $$;

DROP TABLE public.security_rollback_table_postgres, public.security_rollback_table_admin;
DROP SEQUENCE public.security_rollback_sequence_postgres, public.security_rollback_sequence_admin;
DROP FUNCTION public.security_rollback_function_postgres(), public.security_rollback_function_admin();
