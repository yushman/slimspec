---
name: debug
description: "Start a slimspec change from a bug: a debugger agent finds the root cause first, then `explore.md` is written from it and the cycle continues (plan, apply, verify, ground). Use for /slimspec:debug or to fix a bug with slimspec instead of explore."
argument-hint: "[fast | medium | full] <bug description>"
---

# debug

Input: `$ARGUMENTS` — the bug description; a leading `fast`, `medium` or `full` pins the mode. Read `${CLAUDE_PLUGIN_ROOT}/skills/slimspec/protocol.md` first.

```
debug ──gate──▶ plan ──gate──▶ apply ──▶ verify ──▶ ground
```

Debug replaces explore for bugs: no fix before a confirmed root cause; debug writes only `explore.md` — no code, tests or tasks.

## 1. Investigate

Nothing is written until step 2. Launch `slimspec:debugger` with the bug description, the test command and `spec.format`.

- **BLOCKED** — ask its `questions` (steps, environment, logs); relaunch with the original prompt, all answers so far and its `rejected`. Still no root cause → ask: another round / a change that only adds diagnostic logging / abandon (nothing to delete).
- **DONE** — keep the report; it is the design's evidence.

Mode not pinned — suggest one by the size of the fix and confirm, by the criteria of explore step 1 (usually `fast`).

## 2. Gate

More than one viable fix direction (e.g. at the symptom vs at the origin) → ask which, the debugger's direction recommended; in `fast` at most 3 questions, as in explore.

- **medium, full** — first present the walkthrough in chat (no file), detailed enough to approve without opening files:
  - symptom and repro: observed vs expected
  - root cause, citing `path:line`, with its evidence
  - rejected hypotheses and why
  - fix direction; ASCII diagram where data or control flow changes
  - touched modules, files, public contracts; risks

  Then ask: finalize / change fix direction / investigate further (what to check); change fix direction → ask for it, then present the walkthrough again; investigate further → relaunch the debugger with the original prompt, all answers so far, its `rejected` and what to check.
- **fast** — no offer; plan holds the combined gate.

Pick the slug, create `.slimspec/changes/<slug>/` with the `.gitignore` handling of protocol "Change folder" and write `explore.md` there from `${CLAUDE_PLUGIN_ROOT}/skills/slimspec/explore-template.md`:

- **Goal** — the bug is gone, observable; the repro is the first task's `test-first`.
- **Decisions** — the root cause with its evidence (`path:line`) as context, the fix direction as choice, rejected hypotheses as rejected alternatives.
- **Risks** — what the investigation left unconfirmed. Diagnostic-logging change: Goal is the logging at the boundaries the debugger named, the unknown root cause a risk.

- **full** — show `explore.md` in full; ask to approve or name changes until approved.

## 3. Continue

Read `${CLAUDE_PLUGIN_ROOT}/skills/slimspec/SKILL.md` and follow it for `<slug>`; it resumes with plan.
