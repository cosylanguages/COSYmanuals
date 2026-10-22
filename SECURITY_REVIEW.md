# Security review and safe publishing

## Current access model

The current SQL schema enables RLS on `public.manual_content` and defines a SELECT policy for the Supabase `authenticated` role. That policy permits every authenticated user to read every row. This is appropriate only if all signed-in users are entitled to all manuals. It is not per-course, per-subscription, or per-role authorization.

The publishing script uses the Supabase service-role key. Treat it as a privileged secret: never place it in browser code, public CI logs, committed files, or a public `.env.example`. The key bypasses RLS in standard Supabase configurations, so publisher safety depends on protecting the execution environment.

## Required verification before production

Run these read-only queries in the intended Supabase project and inspect the results with an administrator. Do not apply schema changes to production as part of an unreviewed audit.

```sql
-- Confirm RLS is enabled.
select n.nspname as schema_name, c.relname as table_name, c.relrowsecurity as rls_enabled,
       c.relforcerowsecurity as rls_forced
from pg_class c
join pg_namespace n on n.oid = c.relnamespace
where n.nspname = 'public' and c.relname = 'manual_content';

-- Inventory every policy; permissive policies are combined with OR.
select schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
from pg_policies
where schemaname = 'public' and tablename = 'manual_content'
order by policyname;

-- Inspect table grants. RLS does not grant table privileges by itself.
select grantee, privilege_type
from information_schema.role_table_grants
where table_schema = 'public' and table_name = 'manual_content'
order by grantee, privilege_type;
```

## Expected policy decisions

- Anonymous users: no SELECT or write access to gated manual content.
- Authenticated users: SELECT only if the product intentionally grants all signed-in users access to every manual. Otherwise implement and test the actual entitlement rule before release.
- Publishing role: write access only from the trusted publisher. Prefer the built-in service role only in a trusted server-side environment.
- Other roles: no INSERT, UPDATE, or DELETE unless explicitly required.

RLS policies are permissive by default: one unexpected additional permissive policy can broaden access. Review the full policy inventory, not just the policy created by this repository's schema file.

## Safe validation workflow

1. Validate catalog metadata and run automated tests locally.
2. Run the publisher only with `--dry-run` when reviewing intended writes; never provide a production service-role key to tests.
3. Test real authorization behavior in a non-production Supabase project using anonymous, authenticated, and publisher credentials.
4. Verify that failed requests produce a non-zero process exit status and that no secret appears in logs.
5. Only after review, apply approved database changes through the project's normal migration process.

This document is a checklist, not proof that the deployed database matches the repository schema. Live project settings and all policies must be inspected directly.
