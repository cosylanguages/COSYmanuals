-- Disposable PostgreSQL fixture for the proposal test only.
-- This is NOT a Supabase staging substitute; auth.uid() and the minimal catalog are stubbed.
CREATE ROLE anon NOLOGIN;
CREATE ROLE authenticated NOLOGIN;
CREATE ROLE service_role NOLOGIN;
CREATE ROLE supabase_admin NOLOGIN;

CREATE SCHEMA auth;
CREATE TABLE auth.users (id uuid PRIMARY KEY);

CREATE OR REPLACE FUNCTION auth.uid()
RETURNS uuid LANGUAGE sql STABLE
AS $$ SELECT NULLIF(current_setting('request.jwt.claim.sub', true), '')::uuid $$;

CREATE TABLE public.profiles (
  id uuid PRIMARY KEY REFERENCES auth.users(id),
  role text NOT NULL
);

CREATE OR REPLACE FUNCTION public.is_founder()
RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER
SET search_path = public
AS $$ SELECT EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'founder') $$;
GRANT EXECUTE ON FUNCTION public.is_founder() TO anon, authenticated, service_role;

CREATE TABLE public.lesson_notes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  room_key text NOT NULL,
  lesson_id text NOT NULL,
  content text DEFAULT '',
  version integer DEFAULT 0,
  participants uuid[] DEFAULT '{}',
  created_by uuid REFERENCES auth.users(id),
  updated_by uuid REFERENCES auth.users(id),
  updated_at timestamptz DEFAULT now(),
  CONSTRAINT lesson_notes_room_lesson_key UNIQUE (room_key, lesson_id)
);
ALTER TABLE public.lesson_notes ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Participants and founders can read lesson notes" ON public.lesson_notes
  FOR SELECT USING (auth.uid() = ANY(participants) OR public.is_founder());
CREATE POLICY "Participants can update lesson notes" ON public.lesson_notes
  FOR UPDATE USING (auth.uid() = ANY(participants)) WITH CHECK (auth.uid() = ANY(participants));
CREATE POLICY "Authenticated users can insert lesson notes if in participants" ON public.lesson_notes
  FOR INSERT WITH CHECK (auth.uid() IS NOT NULL AND auth.uid() = ANY(participants));

CREATE TABLE public.manual_content (manual_id text PRIMARY KEY, markdown_content text);
CREATE TABLE public.lesson_content (id text PRIMARY KEY);
CREATE TABLE public.student_lesson_content (id text PRIMARY KEY);

GRANT ALL ON public.manual_content, public.lesson_content, public.student_lesson_content TO anon, authenticated, service_role;
GRANT ALL ON public.lesson_notes, public.profiles TO anon, authenticated, service_role;
GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;
GRANT USAGE ON SCHEMA auth TO anon, authenticated, service_role;
GRANT SELECT ON auth.users TO anon, authenticated, service_role;
GRANT CREATE ON SCHEMA public TO supabase_admin;

-- Simulate the broad per-schema defaults observed in the read-only project catalog.
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON TABLES TO anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES TO anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT EXECUTE ON FUNCTIONS TO anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT ALL ON TABLES TO anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT ALL ON SEQUENCES TO anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT EXECUTE ON FUNCTIONS TO anon, authenticated, service_role;

-- Match the audited database's global function default: no PUBLIC EXECUTE grant.
ALTER DEFAULT PRIVILEGES FOR ROLE postgres REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;

INSERT INTO auth.users (id) VALUES
 ('00000000-0000-0000-0000-00000000000a'),
 ('00000000-0000-0000-0000-00000000000b'),
 ('00000000-0000-0000-0000-00000000000c'),
 ('00000000-0000-0000-0000-00000000000f');
INSERT INTO public.profiles (id, role) VALUES
 ('00000000-0000-0000-0000-00000000000a', 'student'),
 ('00000000-0000-0000-0000-00000000000b', 'student'),
 ('00000000-0000-0000-0000-00000000000c', 'student'),
 ('00000000-0000-0000-0000-00000000000f', 'founder');
