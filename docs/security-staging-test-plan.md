# Staging verification plan: lesson-note RPCs and content grants

Status: **not executed**. This plan requires an isolated disposable database or an explicitly confirmed staging environment. The connected Supabase project currently has no development branches and is treated as potentially production. No live data should be used for adversarial tests.

## Preconditions

- [ ] Identify an isolated staging/disposable database and record its project/environment identifier.
- [ ] Snapshot schema, policies, table ACLs, default ACLs, and function definitions before applying a migration.
- [ ] Create test accounts: participant A, participant B, unrelated signed-in user C, and a founder test account. Do not use real learner accounts.
- [ ] Record the intended founder behavior and confirm the room key is a bearer capability.
- [ ] Capture the current client contract in `COSYplatform-source/classroom.html`: join expects a row; save consumes `version`, `content`, and `conflict`; RPC errors retain a local copy.
- [ ] Apply the candidate SQL only to this isolated environment, after syntax validation.

## RPC authorization tests

| Case | Setup / action | Expected result |
|---|---|---|
| Unauthenticated join | Call join RPC without a user JWT | Rejected; no row created |
| Invalid room key | Authenticated user supplies malformed key | Rejected; no row created |
| Valid first join | A joins with a generated valid 32-hex room key and lesson ID | One row returned; A is a participant |
| Repeat join | A joins the same room and lesson again | Same row; no duplicate participant |
| Second valid join | B joins using the same room key and lesson ID | B is added; existing note content/version retained |
| Unrelated guessed ID | C attempts save with an existing note UUID but is not a participant/founder | Access denied; content/version unchanged |
| Participant save | A saves with the current base version | Success; content updated; version increments once |
| Version conflict | A saves with stale or future base version | Conflict=true; current version/content returned; no overwrite |
| Founder access | Founder tries read/save according to approved product policy | Exactly the documented policy; no broader access granted |
| Unauthenticated save | No user JWT | Rejected; content/version unchanged |
| Cross-room isolation | A tries to save B's unrelated room note by UUID | Denied unless A is a participant or approved founder |
| Concurrent saves | Two participants save from the same base version | One succeeds; the stale writer receives a conflict |

For every denied write, assert the persisted row is unchanged. Do not treat a client-side PeerJS handshake as database authorization. The room key is a bearer secret; tests must not print real keys or tokens in logs.

## Grant and entitlement regression tests

- [ ] Verify `anon` and `authenticated` lack table-level `TRUNCATE`, `REFERENCES`, `TRIGGER`, and `MAINTAIN` on `manual_content`, `lesson_content`, and `student_lesson_content`.
- [ ] Confirm expected `SELECT/INSERT/UPDATE/DELETE` grants for actual publisher, author, and reader paths before applying any revoke.
- [ ] Confirm RLS remains enabled and policies unchanged unless a separately reviewed policy migration is approved.
- [ ] Exercise `manual_content` entitlement cases: founder, teacher with permitted language, student with permitted language/level, and unauthorized language/level. No blanket authenticated policy.
- [ ] Test lesson read paths, author writes, publisher writes, and student lesson access through the actual Data API/client roles.
- [ ] Inspect default ACLs for every table-creator role. The live inventory includes `postgres` and `supabase_admin`; check whether any additional owner roles create public tables.
- [ ] Confirm future tables created by each owner receive no unintended implicit client grants, and that required minimal grants are added explicitly in migrations.
- [ ] Verify service-role/backend workflows still work without broadening client grants.

## Rollback plan (staging first)

Prepare and review the rollback script **before** applying the candidate migration. Do not use a guessed inverse migration: the current ACL state includes grants that may be intentional, and default privileges are scoped to the role that creates each object.

1. Capture a timestamped, access-controlled baseline for the exact environment: migration/version history; function definitions via pg_get_functiondef and function ACLs for every function changed; table/sequence ACLs; default ACLs for every role that can create objects in public; RLS enablement and policy definitions; relevant table constraints; and current security-advisor output. Record the project/environment identifier and database version. Do not include learner content, JWTs, or room secrets in artifacts.
2. Generate a rollback script from that baseline. It must restore the exact prior function definitions, function EXECUTE ACLs, table/sequence ACLs, and per-creator default ACLs. Include explicit policy/constraint restoration only if the forward migration changes them. Review the script independently and check it into the same review before the forward change is considered releasable.
3. On isolated staging, use a transaction for DDL/ACL changes where supported and appropriate. Run syntax/definition checks first. Abort on the first error; do not run partial statements manually to force completion. If any operation cannot be transactional in the target environment, document it and define its recovery step before applying.
4. If a release gate fails, stop further rollout. Run the reviewed rollback script against the same environment, inspect every statement result, then compare restored function definitions, ACLs, default ACLs, RLS state, and policies to the baseline. A rollback is not complete merely because the script exits successfully.
5. Re-run the RPC authorization, concurrent version-conflict, entitlement, author/publisher, service-role, and browser regression tests after rollback. Confirm content and version values match pre-test fixtures and that no test-only accounts or data remain.
6. Save sanitized evidence: before/after catalog snapshots, test results, advisor output, migration and rollback checksums, reviewer sign-off, and residual risks. Do not promote to production until an independent reviewer signs off on the forward diff, rollback diff, test evidence, and explicit production authorization.

### Rollback-specific assertions

- [ ] anon, authenticated, service_role, and object-owner behavior matches the captured baseline/approved design; do not blindly revoke or restore broad service-role privileges.
- [ ] Default ACLs are restored separately for every object-creating role and schema. Restoring only postgres defaults is insufficient if migrations also run as supabase_admin or another owner.
- [ ] No rollback step drops or truncates lesson/content tables or deletes live content.
- [ ] If a forward migration has already changed note rows, do not assume restoring function definitions/ACLs reverses those row changes. The proposed remediation should not be treated as data-reversible without a separately reviewed data-recovery plan.

## Release gates

- [ ] SQL syntax/definition validation passes on isolated staging.
- [ ] All RPC authorization and version-conflict tests pass.
- [ ] Entitlement and publisher regressions pass.
- [ ] Security advisor findings are reviewed; any accepted residual findings are documented.
- [ ] Browser workflow passes keyboard, responsive, accessibility, and print/PDF checks.
- [ ] Migration and rollback are independently reviewed.
- [ ] Production deployment is a separate, explicitly approved action.


## Non-billable preflight: disposable PostgreSQL CI harness

The repository quality workflow now runs the proposed SQL against a fresh PostgreSQL 17 service container, then runs assertions and a fixture-only rollback. This uses the ephemeral GitHub Actions runner, not a Supabase development branch or the connected project.

The harness covers SQL parsing/execution against a minimal schema, unauthenticated and malformed joins, first/repeat joins, participant membership, unauthorized saves, version-zero initialization, successful save/version increments, stale-version conflict behavior, founder RPC behavior, the intended note-RPC EXECUTE matrix, dangerous content-table privileges, service-role publisher INSERT, and default ACL behavior for new objects created by both postgres and supabase_admin.

**Limitations:** auth.uid() and the minimal Supabase catalog are stubbed. The harness does not validate the actual Supabase Data API, JWT claim plumbing, platform-managed roles, every live RLS policy, actual browser behavior against a backend, or concurrent transactions. Its rollback restores the known test fixture baseline only; it is not a production rollback script. Passing CI is a useful non-billable SQL/logic preflight, not a substitute for the required isolated Supabase staging run.

## Required access/role matrix before a real staging run

- `anon`: only the explicitly intended public read paths and session-token redemption; no note RPC execution, content writes, or dangerous table privileges.
- `authenticated` student: only entitlement-matched manual/student-safe content; may join a note only if the bearer-room-key policy is explicitly approved; may save only notes where their UID is a participant.
- `authenticated` teacher/lesson author: preserve language-authorized read and explicitly intended authoring/publishing operations; verify `is_lesson_author()`-dependent policies individually.
- `authenticated` founder: preserve founder administration and the exact approved note read/save behavior; verify every policy that depends on `is_founder()`.
- `service_role` / trusted publisher: preserve the server-side `scripts/publish_to_supabase.js` upsert path; never expose the service-role key to browsers or ordinary client roles.
- object owners (`postgres`, `supabase_admin`, plus any additional creator roles found in the target): verify defaults independently for tables, sequences, and functions. Do not alter platform-managed schemas as part of this public-schema proposal.

The room key is a bearer capability in the current client. Product approval must explicitly answer: **Is possession of the 32-hex key alone sufficient to join, or must a trusted invitation/enrollment check also be required?** Until that decision is recorded, the join RPC change is not deployment-ready.

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
