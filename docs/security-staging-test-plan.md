# Staging verification plan: lesson-note RPCs and content grants

Status: **not executed**. This plan requires an isolated disposable database or an explicitly confirmed staging environment. The connected Supabase project currently has no development branches and is treated as potentially production. No live data should be used for adversarial tests.

## Preconditions

- [ ] Identify an isolated staging/disposable database and record its project/environment identifier.
- [ ] Snapshot schema, policies, table ACLs, default ACLs, and function definitions before applying a migration.
- [ ] Create test accounts: participant A, participant B, unrelated signed-in user C, and a founder test account. Do not use real learner accounts.
- [ ] Record the intended founder behavior and confirm the live-lesson note join policy: is the 32-hex room key itself the invitation credential, or must the server also verify a trusted live-lesson roster/invitation?
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
- `authenticated` student: only entitlement-matched manual/student-safe content; may join collaborative notes for a live lesson only under the explicitly approved room-invitation / live-lesson membership policy; may save only notes where their UID is a participant.
- `authenticated` teacher/lesson author: preserve language-authorized read and explicitly intended authoring/publishing operations; verify `is_lesson_author()`-dependent policies individually.
- `authenticated` founder: preserve founder administration and the exact approved note read/save behavior; verify every policy that depends on `is_founder()`.
- `service_role` / trusted publisher: preserve the server-side `scripts/publish_to_supabase.js` upsert path; never expose the service-role key to browsers or ordinary client roles.
- object owners (`postgres`, `supabase_admin`, plus any additional creator roles found in the target): verify defaults independently for tables, sequences, and functions. Do not alter platform-managed schemas as part of this public-schema proposal.

The room key is a bearer capability in the current client. Product clarification on 2026-10-22 establishes that `lesson_notes` are collaborative COSYplatform notes used during live lessons, separate from manuals. It does **not** establish a paid-session requirement. The remaining authorization decision is: **Is possession of the 32-hex room key the intended live-lesson invitation credential, or must the server also verify a trusted live-lesson roster/invitation?** Until that is recorded, the join RPC change is not deployment-ready.

## Product clarification: live-lesson collaboration, not manual access

The notes are used collaboratively during live lessons. Do not apply the manuals' language/level access rule to notes as a substitute for live-lesson participation, and do not add a paid-session entitlement gate based on the earlier mistaken statement.

The current `classroom.html` client sends `room_key` and `lesson_id` (the latter is `currentLessonPath || 'default'`) to `join_lesson_note`; it does not send a session ID. The room key is generated client-side, and `lesson_notes` has no authoritative session ID or room-to-session mapping. The current RPC treats the key as a bearer invitation and adds any authenticated caller presenting it as a participant. The browser-side PeerJS handshake is not a database authorization boundary.

Before changing `join_lesson_note`, confirm how live-lesson participants receive room keys and whether possession of the key is intentionally sufficient. If a trusted roster/invitation check is required, first identify the authoritative live-lesson membership source and server-side mapping from room to lesson/session. Do not infer note authorization from manual access, a generic language/level read grant, a client-supplied flag, or an unverified client-supplied session ID.

Update the disposable SQL tests to match the approved policy: include authorized live-lesson participants, unrelated authenticated users who know or guess a key, malformed keys, repeated joins, participant-only saves, and version conflicts. If key possession is explicitly approved as the invitation credential, document the key-distribution, leakage, rotation/expiry, and rate-limiting expectations. CI success must not be interpreted as approval to deploy the current draft.
