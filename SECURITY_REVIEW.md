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

**Important design blocker:** the canonical client uses a 32-hex-character room key as a bearer capability: a signed-in user who obtains the key can join and become a participant. The proposal now preserves that flow while adding authentication, input validation, and a hardened RPC search path. This is not equivalent to a trusted invitation/enrollment check; product owners must explicitly confirm that possession of the room key is sufficient authorization, and review leakage, expiry/rotation, and rate limiting before deployment. Test first-time and repeat joins, nonparticipant reads/writes, unauthenticated calls, version conflicts, and founder/author workflows in staging.

The grant section is intentionally incomplete for deployment: verify all existing grants, table owners and default-privilege owners, and all required SELECT/INSERT/UPDATE/DELETE paths. Preserve the entitlement-aware `manual_content` policy. Run the Supabase security advisor again after staged changes, and prepare rollback before any production migration.


### Follow-up source review: classroom note-join contract

A read-only review of the canonical `COSYplatform-source` `classroom.html` and `supabase/migrations/0009_lesson_notes.sql` clarified the intended join contract. The client generates a 10-character room ID and a separate 32-hex-character secret room key; after its client-side PeerJS handshake it calls `join_lesson_note`, which creates the note if missing or adds the authenticated caller to `participants`. The browser handshake is not a database authorization boundary: a signed-in user who obtains the room key can join the note room.

The proposal in `docs/security-remediation-proposal.sql` drafts authentication checks, key-format validation, an empty `search_path`, and participant-only saves (plus founders if existing product policy permits them). Product clarification now establishes that these are collaborative COSYplatform notes used during live lessons, separate from manuals; it does not establish a paid-session gate. The current draft still treats the room key as a bearer invitation, and that specific authorization assumption must be confirmed before deployment. The save response is aligned with the client contract, which consumes `version`, `content`, and `conflict`.

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

### Default-privilege scope and helper-function dependencies

A follow-up read-only catalog query confirms default ACL entries for `public` tables, sequences, and functions under both `postgres` and `supabase_admin`. The draft proposal now includes default-privilege revokes for all three object types under those two roles. This is intentionally fail-closed and is not a drop-in production migration: each migration must explicitly grant the exact required table/sequence privileges and function EXECUTE rights, and all roles that can create public objects must be inventoried first. The inventory also shows defaults in other schemas; the proposal is scoped to `public` and must not be broadened to platform-managed schemas without a separate review.

Read-only effective-privilege checks also show `anon` currently has table-level SELECT on several tables whose RLS policies reference `is_founder()` or `is_lesson_author()` (including `lesson_content`, `manual_content`, `lesson_authors`, and others). That does not alone prove data exposure—the policies and function behavior matter—but it means helper EXECUTE grants and each affected policy must be reviewed together. Do not revoke helper execution or change its search path in isolation without testing every dependent RLS policy and supported anonymous/authenticated access path.

The proposed migration still does not remediate existing grants on `is_founder()`, `is_lesson_author()`, or `redeem_session_access_link(...)`; it only proposes safer defaults for newly created functions. These existing functions require a separate reviewed change that preserves intentional policy evaluation and session-link redemption. No database changes were made.

### Final pre-deployment review checkpoint

- GitHub Actions for PR head `45ed41b10e1ceb2668ac6832b78fea2d29d3b6a4` completed successfully: Link Check and Repository quality checks (including the browser smoke job). Subsequent security-document/proposal edits require fresh CI on the newest head before merge.
- Source migration `COSYplatform-source/supabase/migrations/0009_lesson_notes.sql` initializes note versions at `0`, and `classroom.html` uses a local fallback record with version `0`. The proposal was corrected to preserve version-zero initialization. Treat this as an important client/data contract; do not reset existing rows or version counters as part of this change.
- `public.is_founder()` is SECURITY DEFINER with `search_path=public`, executable by `anon` and `authenticated`; `public.is_lesson_author()` is SECURITY DEFINER with `search_path=public` and has a PUBLIC EXECUTE grant; `public.redeem_session_access_link(text,text)` is SECURITY DEFINER with an empty search path and executable by `anon` and `authenticated`. Redemption is intentionally a public-token flow, so do not revoke it blindly. Review its token entropy, rate limiting, use-count race behavior, expiry/revocation checks, and returned fields; preserve intended public redemption while restricting unrelated helper functions as policy dependencies permit.
- The `public` RLS policies referencing `is_founder()` and `is_lesson_author()` span access grants, CMS overrides, CRM tables, lesson answers/authors/content/notes/submissions, manual and student-safe content, profiles, role changes, session catalog/content/grants/revisions/sources/teacher notes, teacher languages, and teacher-student relations. Some policies apply to `PUBLIC` and some only to `authenticated`; capture the full policy inventory in staging and test anonymous, authenticated non-founder, teacher, student, lesson-author, founder, and service-role behavior before changing helper ACLs or search paths.
- Publisher workflow review: `scripts/publish_to_supabase.js` uses `SUPABASE_SERVICE_ROLE_KEY` and upserts `manual_content` through the service-role API. Preserve this server-side publisher path; never replace its key with an anon/authenticated client or expose the key in CI logs. Reader access remains controlled by the existing `Entitled users read manual content` RLS policy and its founder/teacher/student language/level rules.
- No approved non-billable staging environment is available through the connected Supabase project. The project's existing public schema has create permission limited to owner/admin roles, and `private` schema is not available to `anon`; do not attempt to create a test schema or role on the live project as a workaround. A local ephemeral PostgreSQL/Supabase-compatible harness can provide useful parser/behavior tests, but it does not replace staging against the real Supabase auth/RLS/Data API configuration.

Deployment gate remains blocked until current-head CI is green, the room-key bearer capability is explicitly accepted, the helper/RLS grant matrix is approved, and the candidate plus exact rollback have passed in a confirmed isolated environment. No Supabase migration or database modification has been made.

### Catalog dependency inventory and legitimate publisher/reader paths

A grouped read-only `pg_policies` inventory found **32 policies across 22 public tables** whose expressions reference `public.is_founder()`, **3 policies on `lesson_content`** that reference `public.is_lesson_author()`, and **1 policy on `profiles`** that references `private.is_founder()`. The public-founder policy set covers access grants, CMS overrides, CRM activities/contacts/deals, lesson answers/authors/content/notes/submissions, manual content, profiles, role changes, session catalog/content/grants/revisions/sources/teacher notes, teacher languages, and teacher-student relations. Policies apply to different role sets (`PUBLIC`, `anon`/`authenticated`, or `authenticated` only), so one global helper ACL change cannot be assumed safe.

Effective function ACLs observed read-only:

- `public.is_founder()`: SECURITY DEFINER, `search_path=public`; EXECUTE granted to `anon`, `authenticated`, and `service_role`.
- `public.is_lesson_author()`: SECURITY DEFINER, `search_path=public`; explicit EXECUTE to `anon`, `authenticated`, `service_role`, and `PUBLIC`.
- `private.is_founder()`: SECURITY DEFINER, empty search path; EXECUTE to `authenticated` and `service_role`, not `anon`. The `private` schema is not usable by `anon`.
- `public.redeem_session_access_link(text,text)`: SECURITY DEFINER, empty search path; EXECUTE to `anon`, `authenticated`, and `service_role`. This is an intended token-redemption entry point; preserve its public use if product requirements depend on share links, but review token entropy, throttling, expiry/revocation and returned data. `session_access_links` has RLS enabled and no direct policies, so the definer function is the relevant access path.

Read-only policy/grant matrix for content tables:

- `manual_content`: reader policy is authenticated entitlement-based (founder, teacher language access, student language and level). A separate `service_role` ALL policy supports the trusted publisher. `scripts/publish_to_supabase.js` uses the service-role key for `INSERT ... on_conflict=manual_id` upserts, so backend publisher INSERT/UPDATE must continue to work. The connected project currently gives `anon` SELECT table privilege, but no anon-targeted RLS policy was found on this table; table privilege alone does not mean anon can read rows.
- `lesson_content`: author INSERT/UPDATE and read policies depend on `is_lesson_author()`; delete is founder-only; separate reader policies cover founder and entitled teachers. Anonymous table-level SELECT/INSERT privileges do not bypass RLS, but function execution errors or changed helper behavior can break policy evaluation.
- `student_lesson_content`: the existing authenticated reader policy is entitlement-based for founder/teacher/student language and level. Do not replace it with blanket authenticated access.

These findings support a staged approach: preserve existing policy expressions and table grants for ordinary CRUD until the role matrix is tested; revoke only the dangerous table-level privileges in the candidate proposal; harden helper search paths and EXECUTE grants in a separately reviewed policy-aware change. Test anonymous requests, ordinary authenticated users, teachers/authors, students, founders, and the trusted service-role publisher against each affected table. No live permissions or policies were changed.

## Confirmed product rule: paid session entitlement gates room joining

The product requirement is now explicit: a user who has paid for / holds a valid entitlement to the relevant session should be allowed to join that session. A room key by itself is not sufficient authorization for an otherwise unentitled user.

Before changing `join_lesson_note`, trace the authoritative paid-session entitlement records and the exact mapping between session, room key, and lesson. The join RPC must verify the authenticated user's active entitlement for that specific session server-side before inserting or appending a participant. Reuse the canonical entitlement/session authorization logic where possible; do not infer payment from possession of a room key, a browser handshake, a client-supplied flag, or a client-supplied session ID that is not independently verified.

Define and test handling for refunded/cancelled/expired/revoked entitlements, duplicate purchases, teacher/founder exceptions, and any complimentary or administrator-granted sessions. Do not broaden access to all paid sessions when the room is tied to only one session.

**Current proposal is not compliant with this newly confirmed rule yet.** Its current `join_lesson_note` only checks authentication and room-key format, then adds the caller as a participant. That bearer-key-only behavior must be replaced with the verified entitlement gate before the proposal can be considered deployment-ready. The current disposable SQL tests validate the existing proposal behavior only and must be updated to include entitled and unentitled callers once the authoritative entitlement relation is mapped.

## Paid-session entitlement gate: confirmed rule and unresolved data binding

Product decision confirmed 2026-10-22: a user with a valid paid entitlement for the relevant session should be allowed to join; possession of the room key alone must not authorize an unentitled user.

Read-only catalog review found `public.session_grants(user_id, session_id, valid_until, source, ...)` and `public.can_read_session(p_session_id text)`. The existing `can_read_session` helper returns true for founders, teachers with the relevant language, currently valid explicit `session_grants`, and currently valid language/level `access_grants` for published sessions. This is useful existing authorization logic, but it represents general read entitlement, not strictly proof of payment.

**Critical integration gap:** the current `classroom.html` RPC call sends `room_key` and `lesson_id`, where `lesson_id` is `currentLessonPath || 'default'`. It does not send a session ID. The current client generates the room key client-side, and the current `lesson_notes` schema has no authoritative session ID or room-to-session mapping. Therefore it is not safe to call `can_read_session(lesson_id)` or trust a client-supplied session ID: there is no verified mapping tying that room key to the paid session.

Before implementing the gate, design a server-authoritative mapping from a room capability to a canonical `session_catalog.session_id` (for example, an explicit room/session record created by a trusted session-creation flow). At join time, resolve the session from that mapping, authenticate the caller, verify the applicable active entitlement server-side, and only then add them as a participant. Decide whether founders/teachers and complimentary grants are permitted exceptions; check `valid_until`, and define refund/cancellation/revocation semantics. Do not equate a generic language/level read grant with payment unless product policy explicitly says that grant is sufficient.

The current SQL proposal remains deliberately incomplete and non-deployable. The disposable PostgreSQL harness only checks the existing draft's current behavior; it does not prove the new paid-entitlement requirement. Add entitled-user, unentitled-user, expired/revoked-grant, wrong-session, and mismatched-room/session cases after the authoritative mapping and policy are implemented. CI success must not be interpreted as approval to deploy this draft.
