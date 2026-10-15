# migrate-superpowers examples

The project from the running example (`${CLAUDE_PLUGIN_ROOT}/skills/slimspec/examples.md`): a TypeScript monorepo with `packages/auth`, `packages/api`, `packages/db`, config defaults (`claude-md`, `unit: auto`). Lockout and session tokens were designed and built with Superpowers.

## Mapping gate

```
## Migrate · superpowers · mapping
| Source | Target spec | Notes |
|---|---|---|
| docs/superpowers/specs/2026-05-12-login-lockout-design.md | packages/auth/CLAUDE.md, packages/db/CLAUDE.md | merge, new |
| docs/plans/2025-11-20-session-tokens-design.md (older layout) | packages/auth/CLAUDE.md | merge |
| docs/superpowers/plans/, .superpowers/ | — | not migrated; cleanup only |
Ambiguous: docs/superpowers/specs/2026-06-01-unlock-email-design.md — no code found → leave out (recommended: never built) / migrate anyway
```

## Design doc → module specs

`2026-05-12-login-lockout-design.md` (excerpt):

```markdown
# Login Lockout Design

## Purpose
Stop password guessing against a single account.

## Approach
Count failures per account in a Postgres table `login_attempts`; 10 failures within 30 minutes lock the account for 30 minutes. All times come from database `now()` so the three replicas agree.

### Approaches considered
- In-memory counters — each replica counts separately.
- Redis — new infrastructure for one feature.

## Out of scope
Per-IP limits (the gateway already does them), an admin unlock UI.

## Testing
Unit tests for the policy with a fake store; route tests for the 429.
```

`packages/auth/CLAUDE.md`:

```markdown
## Lockout
- 10 failed passwords for one account within 30 minutes lock it for 30 minutes.
- Per-IP limiting is the API gateway's job, not this module's.
- State lives in the `login_attempts` table; every time comes from database `now()`, so replicas agree.
```

`packages/db/CLAUDE.md` did not exist — created:

```markdown
# db

Postgres migrations for all packages.

## Tables
- `login_attempts` — one row per account with recent failures. Written only by `packages/auth`.
```

- Not durable, dropped: the approaches considered (their reasons are about the stack at the time), the testing plan, "no admin UI" (absence of a feature).
- Kept: "per-IP limiting is the gateway's job" — a lasting module boundary.
- The older `session-tokens` design said "access token TTL 60 minutes"; the code says 15 → gap `session-tokens#Tokens: access TTL 60 minutes — code disagrees: packages/auth/src/token.ts:8`; the user chose drop; the existing Tokens statement (15 minutes) stays as it is.

## Cleanup gate

```
## Migrate · superpowers · cleanup
Delete:
- docs/superpowers/ — 2 designs, 2 plans
- docs/plans/2025-11-20-session-tokens-design.md, docs/plans/2025-11-20-session-tokens.md
- .superpowers/ — progress ledgers; git-ignored, so not in git history
History of the docs stays in git.
Then uninstall the plugin yourself: /plugin uninstall superpowers@claude-plugins-official
```
