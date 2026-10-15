# ground examples

Change: `login-lockout` after verify passed (artifacts in `${CLAUDE_PLUGIN_ROOT}/skills/slimspec/examples.md`; refine raised the thresholds to 10 failures / 30 minutes). Format `claude-md`, `unit: auto`: each of `packages/auth`, `packages/api`, `packages/db` has a `package.json`, so each is a unit.

## Durable or not

| From the change | Kept? | Why / where |
|---|---|---|
| 10 failures in 30 minutes lock the account for 30 minutes | yes | behavior → auth, Lockout |
| Every time comes from database `now()` | yes | invariant → auth, Lockout |
| `POST /login` answers 429 + `Retry-After` for a locked account | yes | contract → api |
| Lock per account, not per IP, because rotating IPs bypass a per-IP key | yes | decision with its reason → auth |
| Accepted risk: anyone can lock a known account | yes | the accepted cost of that decision, stated next to it |
| Non-goal: per-IP limiting is the gateway's job | yes | a lasting module boundary |
| Non-goal: no admin unlock UI | no | absence of a feature, not module behavior |
| Rejected: Redis — new infrastructure | no | about this project's stack at the time, not a module rule |
| "T2 adds lockout.ts", "wave 2 depends on T1" | no | plan |
| "Started with 5 / 15 minutes, security raised it" | no | history; the spec states only 10 / 30 |
| "Login now returns 429 instead of 401" | not as written | history wording; state the contract in present tense |
| "158 tests passed" | no | log |

## Module spec before and after

`packages/auth/CLAUDE.md` before:

```markdown
# auth

Password login and session tokens for all API routes.

## Login
- `login(email, password)` returns a token pair or throws `InvalidCredentialsError`.
- Unknown email and wrong password give the same error and take the same time: unknown emails are compared against a dummy bcrypt hash.
- Login failures are not tracked; the API gateway's per-IP limit is the only throttle.
- Passwords are hashed with bcrypt, cost 12.

## Tokens
- Access token TTL 15 minutes; refresh token TTL 30 days, rotated on every refresh.
```

After:

```markdown
# auth

Password login and session tokens for all API routes.

## Login
- `login(email, password)` returns a token pair or throws `InvalidCredentialsError` or `AccountLockedError` (`retryAfterSec`).
- Unknown email and wrong password give the same error and take the same time: unknown emails are compared against a dummy bcrypt hash.
- A locked account is rejected before the password is checked.
- Passwords are hashed with bcrypt, cost 12.

## Lockout
- 10 failed passwords for one account within 30 minutes lock it for 30 minutes. The window opens at the first failure; a failure after it closes opens a new one.
- Unknown emails are never counted and never lock.
- A successful login clears the count.
- Keyed by account, not by IP: rotating IPs must not bypass it. Accepted cost: anyone who knows an email can lock that account for 30 minutes.
- Per-IP limiting is the API gateway's job, not this module's.
- State lives in the `login_attempts` table; every time comes from database `now()`, so replicas agree.

## Tokens
- Access token TTL 15 minutes; refresh token TTL 30 days, rotated on every refresh.
```

Operations applied:

- **modify** — the `login()` statement gains `AccountLockedError`; rewritten in place, not appended as a second signature.
- **remove** — "Login failures are not tracked…" is false now; deleted, not left beside the new section.
- **add** — "A locked account is rejected…" under Login; a new `## Lockout` section for the rest.
- **preserve** — the bcrypt, timing and Tokens statements are untouched, word for word, in their original order.
- **rename** — none here. Had T3 renamed `login` to `authenticate`, every mention in the spec would change to the new name and each statement would stay.

`packages/api/CLAUDE.md`, the two route statements modified in place:

```markdown
## Auth routes
- `POST /login` — 200 with tokens; 401 `{"error":"invalid_credentials"}` for any bad email/password pair; 429 `{"error":"account_locked"}` with `Retry-After` (seconds until unlock) for a locked account.
- `POST /session/refresh` — 200 with rotated tokens; 401 for an invalid or expired refresh token; 429 with `Retry-After` for a locked account, issuing no tokens.
```

`packages/db/CLAUDE.md` did not exist — created with a one-line purpose and only what this change establishes:

```markdown
# db

Postgres migrations for all packages.

## Tables
- `login_attempts` — one row per account with recent failures: `account_id` PK, `failed_count`, `window_started_at`, `locked_until`. Written only by `packages/auth`.
```

Root `CLAUDE.md` — unchanged: no decision spans modules.

## Ground summary for the user

```
Ground · login-lockout · closed · no commit (commit: none)
- packages/auth/CLAUDE.md — updated: add Lockout (6 statements) + 1 Login statement; modify login() errors; remove "failures not tracked"
- packages/api/CLAUDE.md — updated: modify POST /login, POST /session/refresh (429 + Retry-After)
- packages/db/CLAUDE.md — created: login_attempts table
```
