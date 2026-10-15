---
name: apply
description: "Implement the open tasks of a planned slimspec change wave by wave with red-green TDD implementer agents. Use when the user runs /slimspec:apply or asks to implement or continue a planned slimspec change."
argument-hint: "[change-slug]"
---

# apply

Input: `$ARGUMENTS` — change slug (ask which when several are active). Read `${CLAUDE_PLUGIN_ROOT}/skills/slimspec/protocol.md` first unless it is already loaded. Tasks live in `tasks.md` (`fast`: the `## Tasks` section of `explore.md`); grammar in `${CLAUDE_PLUGIN_ROOT}/skills/slimspec/tasks-template.md`.

## 1. Prepare

If `base:` is `none` and the project is a git repo with commits, set it to `git rev-parse HEAD`.

## 2. Run waves

Take the first wave that has open tasks (`- [ ]`, including `invalidated:` and `fix:` ones). Earlier waves must be fully done first.

- **medium, full** — launch one `slimspec:implementer` per open task of the wave, all in a single message so they run in parallel. Wait for every report of the wave before the next wave.
- **fast** — launch one `slimspec:implementer` for all open tasks, in order; it returns one report per task.

Implementer prompt: change folder path, task id(s), resolved test command, for reopened tasks the `invalidated:` / `fix:` text plus the reviewer finding it came from.

## 3. Handle reports

Per protocol. Additionally, per DONE report:

- Mark the task `- [x]` and drop its `invalidated:` / `fix:` marker.
- Under the task line write its `evidence:` line from `tdd` (and a `deviations:` line when the report has any), replacing older ones — grammar in `tasks-template.md`. Verify reads evidence only from there, so a resumed session loses nothing.
- Commit per the `commit` setting.

A BLOCKED report that conflicts with a decision in `explore.md` is a design question: after the user answers, run `refine` before relaunching.

Apply is done when no open task remains; return to the router (or, called directly, tell the user `/slimspec <slug>` continues with verify).

## User output

The user sees short lines, never agent YAML. Samples: `${CLAUDE_PLUGIN_ROOT}/skills/apply/examples.md` — read before the first wave.

- **Wave launch** — `Wave <n> · launched <ids>`.
- **Each report** — `Wave <n> · <id> <done | BLOCKED | FAILED> <closed>/<total>` (closed = `- [x]` tasks of the whole change), then for DONE: the red test and its failure → green count, or the `check:` for `test: none`; deviations named.
- **Pause** (BLOCKED, FAILED) — header `Apply paused · <slug> · <closed>/<total>`, the task, the reason in one or two lines, and which tasks of the wave finished. The question follows via `AskUserQuestion` (options from the report, recommendation first), never as text.
- **Completion** — header `Apply done · <slug> · <n>/<n> tasks · <waves> waves`, one line per task (what, red → green or check), deviations, commits, and what runs next.

## Guardrails

- Never edit code yourself; implementers do.
- Never mark a task `- [x]` without a DONE report and its `evidence:` line; never start a wave while an earlier one has open tasks.
- Never widen a task's `files` without the user's answer.
- Never answer an agent's question yourself or ask the user in plain text.

