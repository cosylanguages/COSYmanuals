# Security review and safe publishing

## Live audit findings — 2026-10-22

A read-only inspection was performed against the connected Supabase project **COSYlanguages** (EU West). No data, grants, policies, functions, or schema were changed.

### Critical: broad table privileges and default privileges

The live entitlement policy on `public.manual_content` is more restrictive than the earlier repository description: it checks founder, teacher language access, and student language/level access. Do not replace it with a generic authenticated-user policy.

However, the live ACLs for `public.manual_content`, `public.lesson_content`, and `public.student_lesson_content` grant the `anon` role SELECT, TRUNCATE, REFERENCES, TRIGGER, and MAINTAIN privileges. The `authenticated` role also has TRUNCATE and other non-minimal privileges on those tables. The live default privileges for tables created by `postgres` in schema `public` also grant broad privileges to `anon`, `authenticated`, and `service_role`.

RLS does **not** protect against table-level `TRUNCATE`, and it is not a substitute for table grants. The grant inventory is a critical finding. This audit did not test whether the public REST endpoint exposes a path to invoke TRUNCATE; it did verify the database role privileges themselves.

Before changing grants, check all legitimate app and authoring flows. A safe target is:
- `manual_content`: no access for `anon`; SELECT for `authenticated` subject to the existing entitlement policy; full table access only for the trusted publisher/service role.
- `lesson_content`: no access for `anon`; retain only the CRUD privileges required by authenticated lesson authors and protected by the existing author policies; remove TRUNCATE, REFERENCES, TRIGGER, and MAINTAIN from client roles.
- `student_lesson_content`: no access for `anon`; SELECT for `authenticated` subject to the existing entitlement policy; writes only for the trusted publisher/service role unless a verified workflow requires otherwise.
- Future public-schema tables: default to least privilege, then explicitly grant only the privileges required by each table's API contract. Changing default privileges can affect existing application assumptions, so stage and regression-test it before rollout.

### High: exposed SECURITY DEFINER functions

The security advisor reported three SECURITY DEFINER functions callable by `anon`: `public.is_founder()`, `public.is_lesson_author()`, and `public.redeem_session_access_link(text, text)`. It also reported 13 SECURITY DEFINER functions callable by `authenticated`. Some may be intentional APIs; each must be reviewed individually for authorization checks, fixed search paths, and least-privilege EXECUTE grants. In particular, `join_lesson_note` and `save_lesson_note` have mutable/unset search paths per the advisor. Do not revoke access or change function security blindly, because valid product flows may depend on them.

The advisor also reported RLS enabled with no policies on `public.session_access_links`. Confirm that this table is intentionally accessed only through narrowly checked functions and is not expected to be queried directly.

### Additional performance observations

The performance advisor reported 16 unindexed foreign keys and 19 RLS policies with auth calls that could be wrapped in scalar subqueries to avoid per-row re-evaluation. These are follow-up optimization items, separate from the critical access-control work.

## Read-only verification queries

Run these in the intended project and preserve the output with the change review. Do not apply schema changes to production as part of an unreviewed audit.

```sql
-- RLS status and forced-RLS setting for sensitive content tables.
select n.nspname as schema_name, c.relname as table_name,
       c.relrowsecurity as rls_enabled, c.relforcerowsecurity as rls_forced
from pg_class c
join pg_namespace n on n.oid = c.relnamespace
where n.nspname = 'public'
  and c.relname in ('manual_content', 'lesson_content', 'student_lesson_content');

-- Inspect the policies. Permissive policies combine with OR.
select schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
from pg_policies
where schemaname = 'public'
  and tablename in ('manual_content', 'lesson_content', 'student_lesson_content')
order by tablename, policyname;

-- Check effective table privileges, including privileges that RLS cannot constrain.
select c.relname as table_name,
       has_table_privilege('anon', c.oid, 'SELECT') as anon_select,
       has_table_privilege('anon', c.oid, 'TRUNCATE') as anon_truncate,
       has_table_privilege('authenticated', c.oid, 'TRUNCATE') as authenticated_truncate,
       has_table_privilege('service_role', c.oid, 'SELECT') as service_role_select
from pg_class c
join pg_namespace n on n.oid = c.relnamespace
where n.nspname = 'public'
  and c.relkind = 'r'
  and c.relname in ('manual_content', 'lesson_content', 'student_lesson_content')
order by c.relname;

-- Inspect default privileges for future public-schema tables.
select n.nspname as schema_name, d.defaclrole::regrole as owner_role,
       d.defaclobjtype, d.defaclacl
from pg_default_acl d
join pg_namespace n on n.oid = d.defaclnamespace
where n.nspname = 'public' and d.defaclobjtype = 'r';
```

## Expected authorization behavior

- Anonymous users: no direct access to gated manual or lesson content. Explicit token-based sharing endpoints, if intended, must validate token hash, expiry, revocation, session identity, and returned fields.
- Authenticated users: access only according to the existing role/language/level/course entitlement rules.
- Lesson authors and teachers: only the specific authoring and teaching capabilities assigned by the product.
- Publisher/service role: write access only from a trusted server-side environment; never expose a service-role key to a browser or public CI log.

## Safe validation workflow

1. Confirm whether this connected project is production. No development branches were returned by the branch listing, so do not assume a staging branch is available.
2. Export/record current grants, policies, relevant function definitions, and a recoverable backup before any proposed database change.
3. Reproduce the current app's read, authoring, publishing, and share-link workflows in an isolated staging project.
4. Apply least-privilege grants and default-privilege changes in staging, preserving the existing entitlement policies.
5. Test anonymous, unentitled authenticated, entitled learner, teacher/author, founder, and publisher behavior; confirm no client role has TRUNCATE on content tables.
6. Review SECURITY DEFINER functions individually and run the Supabase security advisor again.
7. Apply an approved migration through the normal deployment process only after staging and regression tests pass.

This report is a snapshot of a read-only live audit, not proof that any proposed fix has been deployed.