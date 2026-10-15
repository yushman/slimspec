# apply output examples

What the user sees during apply. Change: `login-lockout` (tasks in `${CLAUDE_PLUGIN_ROOT}/skills/slimspec/examples.md`), mode `medium`, 4 tasks in 2 waves. Agent YAML stays in the session.

## Progress

```
T1 done 1/4 · check: migrate up/down passed (test: none — migration)
T2 done 2/4 · red "locks the account on the 5th failure within 15 minutes" → green 6 passed
Wave 1 · T1, T2 · suite 131 passed
T4 done 3/4 · red "POST /login returns 429 with Retry-After…" → green 9 passed
T3 done 4/4 · red "rejects a locked account before checking the password" → green 7 passed · deviation: extra helper `clearFailures` in attempts-store.ts
Wave 2 · T3, T4 · suite 152 passed · apply done → verify
```

Task lines come in report order; the counter is closed tasks / all tasks of the change. Called directly (`/slimspec:apply`), the last line ends `→ /slimspec login-lockout continues with verify`.

## Pause on BLOCKED

```
Apply paused · login-lockout · 3/4 · T4 BLOCKED: needs packages/auth/src/index.ts (outside T4 files) to export AccountLockedError
```

Then the agent's question through `AskUserQuestion`:

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

## Pause on a red wave suite

```
Apply paused · login-lockout · 4/4 · Wave 2 suite FAILED: 2 failing in packages/api/src/routes/session.test.ts — likely T4 (login.ts shares the error mapper)
```

Followed by `AskUserQuestion`: reopen T4 with `fix: <failure>` (recommended) / stop.
