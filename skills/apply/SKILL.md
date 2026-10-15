---
name: apply
description: "Implement a planned slimspec change wave by wave with red-green TDD implementer agents. Use for /slimspec:apply or to implement or continue a planned slimspec change."
argument-hint: "[change-slug]"
---

# apply

Input: `$ARGUMENTS` — change slug. Read `${CLAUDE_PLUGIN_ROOT}/skills/slimspec/protocol.md` unless loaded; grammar in `${CLAUDE_PLUGIN_ROOT}/skills/slimspec/tasks-template.md`. Never edit code yourself.

If `base:` is `none` and the project is a git repo with commits, set it to `git rev-parse HEAD`.

## 1. Run a wave

The first wave with open tasks; never start one while an earlier wave has open tasks.

- **medium, full** — one `slimspec:implementer` per open task, all in one message; wait for the whole wave.
- **fast** — one `slimspec:implementer` for all open tasks in order; one report per task.

Prompt: change folder, task id(s), test command; for a reopened task, the finding behind its marker.

## 2. Reports

Per protocol. Each DONE: mark `- [x]`, drop the marker, write the `evidence:` (and `deviations:`) lines from the report — verify reads evidence only there, so a resume loses nothing. Commit per `commit`. BLOCKED on a decision in `explore.md` → after the answer, run `refine` before relaunching. Never widen a task's `files` without the user's answer.

## 3. Wave suite

All tasks of the wave DONE → run the full suite once (implementers run only their own tests). Red → handle as FAILED: name the failing tests and the likely culprit from the wave's reports (whose `files` the failures touch); offer reopening it with `fix: <failure>` first. Green → commit if `commit: wave`; next wave.

No open task left → return to the router, or tell the user `/slimspec <slug>` continues with verify.

## Output

Samples: `${CLAUDE_PLUGIN_ROOT}/skills/apply/examples.md`.

- **Task** — `<id> done <closed>/<total> · red "<test>" → green <result>` (`test: none`: `check <result>`) `· deviation: <item>` when any; closed counts the whole change.
- **Wave** — `Wave <n> · <ids> · suite <result>` (+ commit); after the last wave `· apply done → verify`.
- **Pause** — `Apply paused · <slug> · <closed>/<total> · <id> BLOCKED|FAILED: <reason>`, then the question.
