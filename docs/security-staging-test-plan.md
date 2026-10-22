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

