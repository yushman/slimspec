---
name: apply
description: "Implement a planned slimspec change wave by wave, one red-green TDD implementer agent per lane. Use for /slimspec:apply or to implement or continue a planned slimspec change."
argument-hint: "[change-slug]"
---

# apply

Input: `$ARGUMENTS` — change slug. Read `${CLAUDE_PLUGIN_ROOT}/skills/slimspec/protocol.md` unless loaded; grammar in `${CLAUDE_PLUGIN_ROOT}/skills/slimspec/tasks-template.md`. Never edit code yourself.

If `base:` is `none` and the project is a git repo with commits, set it to `git rev-parse HEAD`.

## 1. Run a wave

The first wave with open tasks; never start one while an earlier wave has open tasks.

- **medium, full** — one `slimspec:implementer` per lane with open tasks (at most `apply.agents` at once; an extra lane starts when one finishes), all in one message; wait for the whole wave.
- **fast** — one `slimspec:implementer` for all open tasks in order.

Prompt: change folder, the lane's open task ids in listed order, test command; for a reopened task, the finding behind its marker. Each implementer returns one report per task.

## 2. Reports

Per protocol. Each DONE: mark `- [x]`, drop the marker, write the `evidence:` (and `deviations:`) lines from the report — verify reads evidence only there, so a resume loses nothing. Commit per `commit`. A BLOCKED or FAILED task stops the rest of its lane (say so); other lanes finish. Relaunch that lane with its still-open tasks. BLOCKED on a decision in `explore.md` → after the answer, run `refine` before relaunching. Never widen a task's `files` without the user's answer.

## 3. Wave suite

All tasks of the wave DONE → run the full suite once (implementers run only their own tests). Red → handle as FAILED: name the failing tests and the likely culprit task from the wave's reports (whose `files` the failures touch); offer reopening it with `fix: <failure>` first. Green → commit if `commit: wave`; next wave.

No open task left → return to the router, or tell the user `/slimspec <slug>` continues with verify.

## Output

Samples: `${CLAUDE_PLUGIN_ROOT}/skills/apply/examples.md`.

- **Task** — `<id> done <closed>/<total> · red "<test>" → green <result>` (`test: none`: `check <result>`) `· deviation: <item>` when any; closed counts the whole change.
- **Wave** — `Wave <n> · A: <ids> · B: <ids> · suite <result>` (+ commit); after the last wave `· apply done → verify`.
- **Pause** — `Apply paused · <slug> · <closed>/<total> · <id> BLOCKED|FAILED: <reason>` (+ `· lane <L> stopped: <ids>` when tasks remain in it), then the question.
