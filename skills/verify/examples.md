# verify report examples

What the main session shows the user after triage. Change: `login-lockout`, mode `medium`, tasks in `${CLAUDE_PLUGIN_ROOT}/skills/slimspec/examples.md`. Built from the reviewer YAML; the YAML itself stays in the session.

## Findings, fix cycle starts

```
## Verify · login-lockout · round 1 · 2 blockers · 1 should-fix · 1 nit

| Check              | Result                                                        |
|--------------------|---------------------------------------------------------------|
| Suite              | 152 passed                                                    |
| Plan conformance   | 4/4 tasks closed · no files outside `files`                   |
| Design conformance | Goal not reached: refresh still issues tokens (blocker 1)     |
| TDD evidence       | 3 red runs, right reasons · 1 exemption: T1 migration, check passed |
| Deviations         | 1, acceptable: T3 extra helper `clearFailures`                |
| Code review        | /code-review, depth medium                                    |
| Skipped            | packages/db: no module spec, its constraints not checked      |

### Blockers
1. packages/api/src/routes/session.ts:31 — refresh issues tokens to a locked account; Goal says no tokens while locked.
   Fix: call `assertNotLocked(accountId)` before `issueTokens`; test "POST /session/refresh returns 429 for a locked account".
   → new task F1 (no task owns the refresh route)
2. packages/api/src/routes/login.ts:48 — the 429 response has no `Retry-After` header.
   Fix: set `Retry-After` to `err.retryAfterSec`.
   → reopen T4

### Should-fix
1. packages/api/src/routes/login.test.ts:61 — the test asserts only the status, which is how blocker 2 passed.
   Fix: assert `Retry-After` equals the remaining lock seconds.
   → reopen T4 (with blocker 2)

### Nits (listed, never fixed by a cycle)
1. packages/auth/src/lockout.ts:12 — thresholds `5` and `900` inline.
   Fix: name them `MAX_FAILURES` and `LOCK_SECONDS`.

### Design / intent
none

Next: fix cycle 1/2 — T4 and F1 go back to apply, then verify again.
```

## Design finding, refine first

In another run, a design or intent finding is listed in its own group and leads into `refine`; the fix cycle waits for it:

```
### Design / intent
1. explore.md Goal "refresh returns 429 while locked" vs packages/api/CLAUDE.md "clients end the session on any 4xx from POST /session/refresh":
   a lock logs the real user out on every device, which no Risk accepts.
   Fix: either answer refresh with 503 + Retry-After while locked, or accept the logout and record it under Risks.
   → refine (question follows)
```

Then `AskUserQuestion` with the decision, and `refine` with the answer.

## Escalation after two fix cycles

A different run, where the fixes kept failing:

```
## Verify · login-lockout · round 3 · 1 blocker still open after 2 fix cycles
1. packages/api/src/routes/session.ts:38 — refresh returns 429 but still rotates the refresh token.
   Fix: return before `rotateRefreshToken`; extend the F1 test to assert the old token stays valid.
```

Followed by `AskUserQuestion`: one more fix cycle / refine / stop here.

## Pass

```
## Verify · login-lockout · round 2 · pass

| Check              | Result                                   |
|--------------------|------------------------------------------|
| Suite              | 158 passed                               |
| Plan conformance   | 5/5 tasks closed · no files outside `files` |
| Design conformance | Goal reached · Decisions respected       |
| TDD evidence       | 4 red runs · 1 exemption (T1)            |
| Deviations         | 1, acceptable                            |
| Code review        | /code-review, depth medium               |
| Skipped            | packages/db: no module spec              |

Nits left: packages/auth/src/lockout.ts:12 — name the thresholds.
Next: ground, running now.
```
