# migrate-openspec examples

The project from the running example (`${CLAUDE_PLUGIN_ROOT}/skills/slimspec/examples.md`): a TypeScript monorepo with `packages/auth`, `packages/api`, `packages/db`, config defaults (`claude-md`, `unit: auto`). Lockout and session tokens shipped through OpenSpec; one change is in flight.

## Mapping gate

```
## Migrate · openspec · mapping
| Source | Target spec | Notes |
|---|---|---|
| openspec/specs/account-lockout/spec.md | packages/auth/CLAUDE.md, packages/api/CLAUDE.md | merge, merge |
| openspec/specs/session-tokens/spec.md | packages/auth/CLAUDE.md | merge |
| openspec/config.yaml context | root CLAUDE.md | 2 facts not there yet |
| openspec/changes/ (1 active, 6 archived) | — | not migrated; cleanup only |
Ambiguous: "Locked response" → packages/api only (recommended: the route owns the status code) / packages/api + packages/auth
```

## Source spec → module specs

`openspec/specs/account-lockout/spec.md` (excerpt):

```markdown
# account-lockout Specification

## Purpose
TBD - created by archiving change add-account-lockout. Update Purpose after archive.
## Requirements
### Requirement: Lock after repeated failures
The system SHALL lock an account for 30 minutes after 10 failed passwords within 30 minutes. The window SHALL open at the first failure. Unknown emails SHALL NOT be counted.

#### Scenario: Tenth failure locks
- **WHEN** a tenth wrong password for one account arrives within 30 minutes of the first
- **THEN** the account is locked for 30 minutes

#### Scenario: Failure after the window
- **WHEN** a wrong password arrives more than 30 minutes after the first failure
- **THEN** a new window opens with a count of 1

### Requirement: Locked response
`POST /login` SHALL return 429 with `Retry-After` in seconds and body `{"error":"account_locked"}` for a locked account.

### Requirement: Lock notification
The system SHALL email the account owner when the account locks.
```

`packages/auth/CLAUDE.md` gains a section; everything else in it is preserved:

```markdown
## Lockout
- 10 failed passwords for one account within 30 minutes lock it for 30 minutes. The window opens at the first failure; a failure after it closes opens a new one.
- Unknown emails are never counted and never lock.
```

`packages/api/CLAUDE.md`, the route statement modified in place:

```markdown
- `POST /login` — 200 with tokens; 401 `{"error":"invalid_credentials"}` for any bad email/password pair; 429 `{"error":"account_locked"}` with `Retry-After` (seconds until unlock) for a locked account.
```

- `SHALL` becomes present tense; both scenarios restate the requirement, so they fold into it.
- The placeholder Purpose carries nothing.
- "Lock notification" has no trace in the code → gap `account-lockout#Lock notification — not found in code`; the user chose drop.

## Summary

```
## Migrate · openspec · specs
- packages/auth/CLAUDE.md — updated: added Lockout (2 statements), Tokens (2 statements)
- packages/api/CLAUDE.md — updated: modified POST /login (429 + Retry-After)
- root CLAUDE.md — updated: added 2 project facts
Gaps: account-lockout#Lock notification — dropped
Left out: none
Commit: none (commit: none)
```

## Cleanup gate

```
## Migrate · openspec · cleanup
Delete:
- openspec/ — 2 specs, config.yaml, 6 archived changes, 1 active change (add-lockout-audit-log: unbuilt, dropped)
- .claude/skills/openspec-*/ — 8 skills
- .claude/commands/opsx/ — 7 commands
Edit:
- CLAUDE.md lines 40–42: "## Workflow — plan changes with `/opsx:propose`, specs in `openspec/specs/` …"
History stays in git.
```
