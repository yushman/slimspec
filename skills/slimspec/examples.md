# Artifact examples

One running change: a TypeScript monorepo (`packages/auth`, `packages/api`, `packages/db`, each with its own `package.json`; tests with `pnpm test`) adds account lockout after repeated failed logins. Slug: `login-lockout`, mode `medium`.

Formats are defined in [explore-template.md](explore-template.md) and [tasks-template.md](tasks-template.md); these examples follow them exactly.

## Filled explore.md

```markdown
# Lock account after repeated failed logins
mode: medium

## Goal
Password guessing against one account is cut off:
- 5 failed passwords for one account within 15 minutes lock it for 15 minutes.
- While locked, `POST /login` and `POST /session/refresh` return 429 with `Retry-After` (seconds until unlock) and issue no tokens.
- A successful login clears the failure count.
- Unknown emails keep returning 401 exactly as today.
Verified by: lockout policy unit tests; route tests for 429 + `Retry-After` on both endpoints.

## Non-goals
- Per-IP rate limiting — the API gateway already limits per IP.
- CAPTCHA, 2FA, unlock emails.
- An admin UI to unlock accounts.

## Decisions
### Counters live in Postgres
- **Context:** the API runs 3 replicas, so counters must be shared; the stack has Postgres and no Redis.
- **Choice:** table `login_attempts` (`account_id` PK, `failed_count`, `window_started_at`, `locked_until`); all times from database `now()`.
- **Rejected:** in-memory map — each replica counts separately, an attacker gets 3× the attempts; Redis — new infrastructure for one feature.

### Lock per account, not per account + IP
- **Context:** the attack seen in monitoring rotates IPs.
- **Choice:** the lock key is `account_id`.
- **Rejected:** account + IP — rotating IPs bypasses the lock.

### Fixed window from the first failure
- **Context:** the window shape decides storage cost.
- **Choice:** the window opens at the first failure; a failure after `window_started_at + 15 min` opens a new window.
- **Rejected:** sliding window — needs one row per attempt and a cleanup job.

### 429 with Retry-After for a locked account
- **Context:** a plain 401 hides the lock; users keep retrying and file support tickets.
- **Choice:** 429, `Retry-After` in seconds, body `{"error":"account_locked"}`.
- **Rejected:** the usual 401 — the client cannot tell the user when to come back.

## Risks
- Anyone who knows an email can lock that account for 15 minutes — accepted; the lock is short, revisit if support sees abuse.
- After 5 tries a 429 reveals that the email is registered — accepted; unknown emails never lock.
- Replica clocks drift — mitigated: all times come from database `now()`.
```

What makes it good: every Goal line is observable and testable; each Decision names what was rejected and why; Risks are either mitigated or explicitly accepted. No process notes ("we discussed", "first I looked at").

## tasks.md at the plan gate

```markdown
# Tasks: Lock account after repeated failed logins
base: none
fix-cycles: 0

## Wave 1 (lane A: packages/db/migrations/* · lane B: packages/auth/src/*)
Lane A is the migration alone. Lane B is the auth package: T3 calls the policy T2 writes, and both test against an in-memory store fake, so neither waits for the table.
- [ ] T1 · lane: A · files: packages/db/migrations/0012_login_attempts.sql · test: none — migration · check: `pnpm db:migrate` then `pnpm db:migrate:down` on an empty database · done: table `login_attempts` exists with the four columns from Decisions
- [ ] T2 · lane: B · files: packages/auth/src/lockout.ts, packages/auth/src/lockout.test.ts · test-first: "locks the account on the 5th failure within 15 minutes" · done: `registerFailure` returns `locked_until` on the 5th failure in a window; a failure after the window opens a new one
- [ ] T3 · lane: B · files: packages/auth/src/login.ts, packages/auth/src/login.test.ts, packages/auth/src/attempts-store.ts · test-first: "rejects a locked account before checking the password" · done: locked → `AccountLockedError` without a bcrypt compare; wrong password → failure recorded; success → count cleared

## Wave 2 (depends: T2 · lane A: packages/api/src/routes/*)
T4 needs only the `AccountLockedError` type from T2.
- [ ] T4 · lane: A · files: packages/api/src/routes/login.ts, packages/api/src/routes/login.test.ts · test-first: "POST /login returns 429 with Retry-After for a locked account" · done: 429 + `Retry-After` in seconds; unknown email still 401
```

No `evidence:` lines yet: every task is open. Apply runs wave 1 as two implementers (lane A: T1; lane B: T2, then T3), then one for T4.

## tasks.md after verify round 1 and a refine

Verify found two implementation issues: `POST /login` sends 429 without `Retry-After` (owned by T4 → `fix:`), and `POST /session/refresh` still issues tokens to a locked account (no task owns the refresh route → `F1` in a new wave). Before apply ran, the user ran `/slimspec:refine login-lockout` with new input: security wants 10 failures and a 30-minute lock. Refine rewrote the thresholds in Goal and Decisions of `explore.md` and invalidated T2 only; T3 and T4 call the policy and do not depend on the numbers. Verify had set `fix-cycles: 1`; the refine approval reset it to 0.

```markdown
# Tasks: Lock account after repeated failed logins
base: 9f3c2ab
fix-cycles: 0

## Wave 1 (lane A: packages/db/migrations/* · lane B: packages/auth/src/*)
Lane A is the migration alone. Lane B is the auth package: T3 calls the policy T2 writes, and both test against an in-memory store fake, so neither waits for the table.
- [x] T1 · lane: A · files: packages/db/migrations/0012_login_attempts.sql · test: none — migration · check: `pnpm db:migrate` then `pnpm db:migrate:down` on an empty database · done: table `login_attempts` exists with the four columns from Decisions
  evidence: red n/a — migration · check "migrate up and down passed on an empty database"
- [ ] T2 · invalidated: thresholds raised to 10 failures / 30-minute lock · lane: B · files: packages/auth/src/lockout.ts, packages/auth/src/lockout.test.ts · test-first: "locks the account on the 10th failure within 30 minutes" · done: `registerFailure` returns `locked_until` (now + 30 min) on the 10th failure in a 30-minute window; a failure after the window opens a new one
- [x] T3 · lane: B · files: packages/auth/src/login.ts, packages/auth/src/login.test.ts, packages/auth/src/attempts-store.ts · test-first: "rejects a locked account before checking the password" · done: locked → `AccountLockedError` without a bcrypt compare; wrong password → failure recorded; success → count cleared
  evidence: red "rejects a locked account before checking the password — FAIL (expected AccountLockedError, got token pair)" · green "7 passed"
  deviations: extra helper `clearFailures` in attempts-store.ts

## Wave 2 (depends: T2 · lane A: packages/api/src/routes/*)
T4 needs only the `AccountLockedError` type from T2.
- [ ] T4 · fix: 429 response has no Retry-After header (login.ts:48) · lane: A · files: packages/api/src/routes/login.ts, packages/api/src/routes/login.test.ts · test-first: "POST /login returns 429 with Retry-After for a locked account" · done: 429 + `Retry-After` in seconds; unknown email still 401

## Wave 3 (depends: T3 · lane A: packages/api/src/routes/session*)
Added by verify: no task owned the refresh route.
- [ ] F1 · fix: refresh issues tokens to a locked account (session.ts:31) · lane: A · files: packages/api/src/routes/session.ts, packages/api/src/routes/session.test.ts · test-first: "POST /session/refresh returns 429 for a locked account" · done: 429 + `Retry-After`; no tokens issued
```

Apply now runs one implementer per lane with open tasks: T2 (wave 1, lane B), then T4 (wave 2), then F1 (wave 3); T1 and T3 stay closed. Reopening deleted the `evidence:` lines of T2 and T4; apply writes fresh ones when each is done again. Verify reads evidence and deviations only from these lines, so a resumed session reviews the same way.

## Good and bad task lines

Good:

```markdown
- [ ] T2 · lane: B · files: packages/auth/src/lockout.ts, packages/auth/src/lockout.test.ts · test-first: "locks the account on the 5th failure within 15 minutes" · done: `registerFailure` returns `locked_until` on the 5th failure in a window
```
One behavior; exact files including the test; the test name is a behavior that fails before the code exists; `done` can be checked by running it.

```markdown
- [ ] T1 · lane: A · files: packages/db/migrations/0012_login_attempts.sql · test: none — migration · check: `pnpm db:migrate` then `pnpm db:migrate:down` on an empty database · done: table `login_attempts` exists
```
The exemption is an allowed kind (migration) and the check is a command anyone can rerun.

Bad, and why:

| Line | Problem |
|---|---|
| `- [ ] T2 · lane: B · files: packages/auth/** · test-first: "lockout works" · done: lockout implemented` | Glob covers the whole package, so no other lane of its wave can touch it; the test name is not a behavior; `done` is not observable. |
| `- [ ] T3 · lane: B · files: packages/auth/src/login.ts · test-first: "rejects a locked account" · done: ...` | The test file is missing from `files`; the implementer is BLOCKED the moment it writes the test. |
| `- [ ] T2 · lane: B · files: packages/auth/src/lockout.ts, packages/api/src/routes/login.ts, ... · test-first: "locks and returns 429" · done: ...` | Two behaviors in two packages: one red run cannot prove both, and the task blocks parallelism. Split into T2 and T4. |
| `- [ ] T4 · lane: A · files: ... · test: none — small change · check: manual` | "Small" is not an exemption (only config, styles, migrations, docs); `manual` names no step. |
| `- [ ] T1 · lane: A · files: packages/db/migrations/0012_login_attempts.sql, packages/auth/src/attempts-store.ts · test: none — migration · ...` | The exemption also covers store code that needs a test. Keep the migration alone in its task. |
| `- [ ] T5 · lane: B · files: ... · test-first: "exports AccountLockedError" · done: ...` | Tautology: it checks structure, not behavior; it passes the moment the symbol exists. |
| `- [ ] T2 — lockout policy (lockout.ts)` | Not the grammar: no ` · ` fields, so the router and implementer cannot read files, test or done. |

## Good and bad lanes

Good: wave 1 above. Each lane is one package, the lanes share no files, and lane B orders T3 after T2 instead of spending a wave on it.

| Wave | Problem |
|---|---|
| `(lane A: packages/auth/src/* · lane B: packages/auth/src/login*)` | Lanes overlap on `login*`; two implementers edit one file at once. Put both tasks in one lane. |
| Four lanes in one wave, one task each | More lanes than `apply.agents` (3), and one task per lane is a cold start per task again. Merge lanes by module or split the wave. |
| `lane: A` T2, T4 · `lane: B` T3 | T3 calls the policy T2 is still writing in another lane, and lane A mixes two packages. Keep a dependency inside one lane. |
