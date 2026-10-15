# apply output examples

What the main session shows the user during apply. Change: `login-lockout` (tasks in `${CLAUDE_PLUGIN_ROOT}/skills/slimspec/examples.md`), mode `medium`, 4 tasks in 2 waves. Agent reports stay YAML and stay in the session; the user sees only these lines.

## Progress

```
## Apply · login-lockout (medium) · 0/4
Wave 1 · launched T1, T2 (parallel)
Wave 1 · T1 done 1/4 — migration 0012_login_attempts; check: migrate up/down passed (test: none — migration)
Wave 1 · T2 done 2/4 — red "locks the account on the 5th failure within 15 minutes" (expected locked_until, got null) → green 31 passed
Wave 2 · launched T3, T4 (parallel)
Wave 2 · T4 done 3/4 — red "POST /login returns 429 with Retry-After…" (expected 429, got 401) → green 148 passed
Wave 2 · T3 done 4/4 — red "rejects a locked account before checking the password" → green 152 passed · deviation: extra helper `clearFailures` in attempts-store.ts
```

Reports arrive in any order within a wave; print each as it comes. The counter is closed tasks / all tasks of the change.

## Pause on BLOCKED

Another run of the same wave:

```
## Apply paused · login-lockout · 3/4
Wave 2 · T4 BLOCKED
Needs packages/auth/src/index.ts (outside T4 files): @acme/auth does not export AccountLockedError.
Wave 2 · T3 done 3/4 — finished before the pause; kept.
```

Then the agent's question, through `AskUserQuestion`, never as text:

```yaml
question: "T4 needs packages/auth/src/index.ts to export AccountLockedError. How to proceed?"
header: "T4 scope"
options:
  - label: "Add index.ts to T4 (Recommended)"
    description: "One export line; no other wave 2 task touches the file."
  - label: "Import from the deep path"
    description: "No scope change, but bypasses the package entry point the api package uses everywhere."
  - label: "Stop apply"
    description: "Leave T4 open; /slimspec login-lockout resumes later."
```

On "add": append the file to T4's `files` in `tasks.md`, relaunch T4 with the original prompt plus the answer. An answer that contradicts a Decision goes through `refine` first.

## Pause on FAILED

```
## Apply paused · login-lockout · 3/4
Wave 2 · T4 FAILED — full suite red before any change: packages/api/src/routes/health.test.ts (outside the change).
```

Followed by `AskUserQuestion`: retry T4 / fix the unrelated failure first / stop.

## Completion

```
## Apply done · login-lockout · 4/4 tasks · 2 waves
- T1 migration 0012_login_attempts — check passed (test: none — migration)
- T2 lockout policy — red → green
- T3 login rejects locked accounts — red → green
- T4 POST /login 429 + Retry-After — red → green
Deviations: T3 extra helper `clearFailures` in attempts-store.ts
Commits: none (commit: none)
Next: verify, running now.
```

Called directly (`/slimspec:apply`), the last line is: `Next: /slimspec login-lockout continues with verify.`
