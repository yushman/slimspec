# explore examples

Running project: a TypeScript monorepo (`packages/auth`, `packages/api`, `packages/db`) behind an API gateway. The change that comes out of these sessions is `login-lockout`; its finished `explore.md` is in `${CLAUDE_PLUGIN_ROOT}/skills/slimspec/examples.md`.

Each sample shows what the main session writes after the scan, then the `AskUserQuestion` call that follows. Free text explains; the decision itself is always the question. Diagrams and previews appear only where options differ in structure.

## Vague idea

> /slimspec "we should do something about brute-force logins"

Login protection, cheapest to strongest:
- gateway per-IP limit — exists (`gateway/config.yaml:14`);
- per-account lockout — counter + 429 on login; 1 package + 1 route;
- CAPTCHA after N failures — provider + frontend; 3 packages + vendor;
- 2FA — enrolment and recovery flow; weeks.

The gateway already limits per IP, so the open question is what to add on top. I would start with per-account lockout: it covers what per-IP misses and stays inside `packages/auth` and one route.

```yaml
question: "Which protection does this change add?"
header: "Scope"
options:
  - label: "Per-account lockout (Recommended)"
    description: "Stops guessing on one account from any IP; small: auth + one route."
  - label: "Lockout + CAPTCHA"
    description: "Also slows credential stuffing across accounts; adds a vendor and frontend work."
  - label: "CAPTCHA only"
    description: "No lockout DoS risk; does not stop a patient attacker on one account."
```

Do not ask about counters, windows or status codes yet — they belong to a branch the user has not chosen.

## Specific problem

> /slimspec "monitoring shows 2k failed logins per minute on admin@; the gateway limit should catch this, why doesn't it?"

Read the code first and check the user's diagnosis against it: the gateway limits 20/min per IP (`gateway/config.yaml:14`), and `login()` keeps no per-account state (`packages/auth/src/login.ts:22-41`). 2k/min from one IP would be cut at 20, so the traffic comes from many IPs — no per-IP setting will stop it. The missing piece is per-account state in `login()`.

Then the first question is the one this finding opens: lock per account or per account + IP.

## Stuck mid-implementation

> /slimspec:explore login-lockout — "doing F1 I noticed a locked user keeps the sessions they already had. Is that OK?"

The change already has `explore.md` and `tasks.md`: skip the scan, read both, the open task and the code around it.

An access token issued before the lock lives up to 15 more minutes (15 min TTL); refresh is already blocked by F1. Goal says "issue no tokens" — it does not say "revoke existing ones". That gap is a decision:

```yaml
question: "Should a lock end sessions that already exist?"
header: "Sessions"
options:
  - label: "Keep them (Recommended)"
    description: "Access tokens expire within 15 min anyway; refresh is blocked. Add a Non-goal."
  - label: "Revoke refresh tokens on lock"
    description: "Closes the gap fully, but anyone can log the real user out on every device."
```

After the answer, run `refine` (here: add "Revoking sessions that existed before the lock" to Non-goals). Do not rewrite `explore.md` from explore.

## Comparing options

> "Postgres or Redis for the counters?"

Get the context the answer depends on, from the brief or one question. Here the brief already has it: 3 API replicas, Postgres in the stack, no Redis.

```
                 Postgres table        Redis INCR + TTL      in-memory map
shared across    yes                   yes                   no — 3× attempts
replicas
new infra        none                  Redis + ops           none
expiry           compare timestamps    TTL                   timers
```

Postgres: shared, and nothing new to run. Ask with a preview per option, since the options differ in shape:

```yaml
question: "Where do failure counters live?"
header: "Storage"
multiSelect: false
options:
  - label: "Postgres table (Recommended)"
    description: "Shared across replicas, no new infrastructure."
    preview: |
      login_attempts
      ├─ account_id         uuid PK
      ├─ failed_count       int
      ├─ window_started_at  timestamptz
      └─ locked_until       timestamptz null
  - label: "Redis"
    description: "Native TTL and atomic INCR; adds a service to run."
    preview: |
      INCR   lockout:{accountId}
      EXPIRE lockout:{accountId} 900
      SET    locked:{accountId} 1 EX 900
  - label: "In-memory map"
    description: "Zero setup; each replica counts separately."
    preview: |
      const attempts = new Map<AccountId, { count: number; since: Date }>()
```

## Open branches and the finalize offer

Keep the open branches visible between questions, e.g.:

```
Resolved: scope (per-account lockout), storage (Postgres)
Open: lock key (account vs account+IP) · window shape · response code
```

When the list is empty, offer to finalize:

```yaml
question: "All branches are resolved. Write explore.md?"
header: "Finalize"
options:
  - label: "Finalize (Recommended)"
    description: "Write .slimspec/changes/login-lockout/explore.md with 4 decisions and 3 risks."
  - label: "Keep exploring"
    description: "Name what still feels open."
```
