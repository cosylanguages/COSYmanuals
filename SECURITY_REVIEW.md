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

### Critical: note RPCs bypass participant checks

Read-only inspection of function definitions and EXECUTE grants found two authenticated-callable `SECURITY DEFINER` functions that do not check the caller's identity or participant membership inside the function:

- `public.join_lesson_note(room_key text, lesson_id text)` inserts a note row for the supplied room/lesson if missing, then returns the matching row. It does not verify `auth.uid()` or that the caller is listed in `lesson_notes.participants`. The underlying table's RLS policies do not constrain SQL executed as the function owner.
- `public.save_lesson_note(note_id uuid, content text, base_version integer)` selects a note by ID, returns its existing content on version conflict, or updates the content and version. It does not verify the caller's participant membership. Because it is SECURITY DEFINER, the table's participant-based UPDATE policy cannot be relied on to protect this function.

Both functions are executable by `authenticated` and not by `anon`. This is a high-confidence authorization defect in the function bodies, although exploitability depends on whether an attacker can obtain/guess a room key or note UUID. Do not run exploit tests against live data.

**Remediation priority:** urgently review and fix in staging. Add explicit `auth.uid() IS NOT NULL` checks and verify participant membership for the exact note/room before reading, creating, returning conflict content, or updating. For `join_lesson_note`, decide how participants are securely enrolled; do not allow a caller to self-create access merely by choosing `room_key`. For `save_lesson_note`, lock and authorize the row before returning any existing content. Set a safe fixed search path (prefer `SET search_path = ''` with schema-qualified references). Add tests for unrelated authenticated users, missing identity, legitimate participants, conflict responses, and writes. Deploy only after staging tests and review.

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

## Prepared remediation draft — not applied

A proposed staging-only SQL migration is available at [`docs/security-remediation-proposal.sql`](docs/security-remediation-proposal.sql). It is documentation for review, not an approved or executed migration. It has **not** been run against Supabase.

The proposal makes the note RPCs require an authenticated caller and existing participant membership, sets an empty `search_path`, and sketches removal of dangerous content-table privileges and broad default grants. It deliberately does not trust knowledge of `room_key` as enrollment proof.

**Important design blocker:** the current `join_lesson_note` RPC creates a note row on demand. The proposal stops that behavior because no trusted invitation/enrollment mechanism has yet been verified. Before any deployment, trace the real client flow and define how legitimate participants are added to `participants`; then test valid first-time joins, existing participant joins, nonparticipant reads/writes, unauthenticated calls, version conflicts, and founder/author workflows in staging.

The grant section is intentionally incomplete for deployment: verify all existing grants, table owners and default-privilege owners, and all required SELECT/INSERT/UPDATE/DELETE paths. Preserve the entitlement-aware `manual_content` policy. Run the Supabase security advisor again after staged changes, and prepare rollback before any production migration.


### Follow-up source review: classroom note-join contract

A read-only review of the canonical `COSYplatform-source` `classroom.html` and `supabase/migrations/0009_lesson_notes.sql` clarified the intended join contract. The client generates a 10-character room ID and a separate 32-hex-character secret room key; after its client-side PeerJS handshake it calls `join_lesson_note`, which creates the note if missing or adds the authenticated caller to `participants`. The browser handshake is not a database authorization boundary: a signed-in user who obtains the room key can join the note room.

The proposal in `docs/security-remediation-proposal.sql` has been revised to preserve that intended bearer-key flow while requiring `auth.uid()`, validating the key format, setting an empty `search_path`, and restricting `save_lesson_note` to participants (plus founders if the existing product policy permits them). It also aligns the save response with the client contract, which consumes `version`, `content`, and `conflict`.

This is still a **review draft only**, not an applied migration. Before approval, verify the founder authorization expectation, key handling/logging/expiry, actual client error handling, and all grant/default-privilege effects. The SQL must be parsed and exercised against a disposable/staging database before any deployment; no database changes have been made as part of this follow-up.


## Staging verification checklist

The detailed test matrix and rollback gates are now in [`docs/security-staging-test-plan.md`](docs/security-staging-test-plan.md). It covers unauthenticated and invalid-key joins, first/repeated/second-participant joins, unauthorized note UUID writes, participant saves, stale/future version conflicts, founder access, concurrent saves, entitlement regression, and rollback verification. It is a plan only; none of those adversarial tests have been run against a database.

### Additional read-only ACL inventory

A further read-only query found broad default table ACLs for both `postgres` and `supabase_admin` in `public`, including grants to `anon`, `authenticated`, and `service_role`. The proposed SQL now addresses the two observed creator roles, but that portion is deliberately **fail-closed**: revoking all future implicit client table grants also removes default SELECT, so each future table migration must explicitly grant only the minimum required operations and retain appropriate RLS. The current content-table ACLs also show client-role TRUNCATE/REFERENCES/TRIGGER/MAINTAIN privileges. The proposal removes those specific dangerous privileges while leaving ordinary CRUD grants for separate review.

The current security-advisor baseline still reports mutable `search_path` on the two note RPCs, public execution of `is_founder()`, `is_lesson_author()`, and `redeem_session_access_link(...)`, 13 authenticated-callable SECURITY DEFINER functions, and `session_access_links` with RLS but no policies. No database change has been made, so a post-fix advisor run is not yet meaningful; rerun it only after a reviewed staging change.

The browser workflow did complete successfully on commit `2019f73e7ac79b540920c629f5dde68288ee31e4`: keyboard focus, responsive overflow, axe WCAG 2.1 A/AA, and A4 PDF generation passed for English and French sample pages. The current PR head contains later documentation-only commits, so rerun CI against the current head before merge.

### Compatibility follow-up: SQL and client behavior (read-only)

A second read-only pass checked the proposal against the live catalog and canonical `classroom.html` client:

- The connected database reports PostgreSQL **17.6**, so the `MAINTAIN` privilege keyword used by the proposal is supported by the server version. This is syntax compatibility only; it does not validate or execute the migration.
- `classroom.html` passes the record's `version` as `base_version`, handles `data.conflict` by merging local and remote text and retrying once, and treats RPC errors as “saved locally.” The proposal's authorization exception is therefore safer than returning a success-shaped response for a denied save. Still test that the local copy survives reload/reconnect and that repeated conflicts do not falsely show “saved.”
- The existing join function initializes new notes at version `1`. The proposal was adjusted to preserve that initial-version contract. Its upsert also now handles a legacy `NULL participants` array without leaving the caller unrecorded.
- The proposal's save routine calls `public.is_founder()`, but the live function is itself `SECURITY DEFINER` with `search_path = public`, and it is executable by `anon` and `authenticated`. Review/fix that helper's search path and intended EXECUTE grants as a separate, explicitly scoped change before relying on it for authorization. Also review `is_lesson_author()` and `redeem_session_access_link(...)`; their public execution/search-path findings are not fully remediated by changing only the two note RPCs.
- The proposal's table-level and default-ACL changes have not been parsed or executed in staging. Confirm every object-creator role and the actual publisher/reader grant matrix first; do not infer that a syntactically valid `REVOKE` preserves application behavior.

These checks remain static/read-only. No migration, grant, policy, function, or lesson-content changes were made in Supabase.
