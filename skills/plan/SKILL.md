---
name: plan
description: "Turn an approved slimspec `explore.md` into `tasks.md` (TDD tasks in waves of parallel lanes), then the plan gate. Use for /slimspec:plan or to plan an explored slimspec change."
argument-hint: "[change-slug]"
---

# plan

Input: `$ARGUMENTS` — change slug. Read `${CLAUDE_PLUGIN_ROOT}/skills/slimspec/protocol.md` unless loaded. Requires `explore.md`; without it, run explore first. No code in this phase.

## 1. Write the plan

- **medium, full** — launch `slimspec:planner` with the change folder, the scanner brief (if this session has it), the test command and `apply.agents`.
- **fast** — write the `## Tasks` section of `explore.md` yourself per `${CLAUDE_PLUGIN_ROOT}/skills/slimspec/tasks-template.md`, usually one wave with one lane.

## 2. Gate

Ask via `AskUserQuestion`: approve / change. In every mode, list each `test: none` exemption separately.

- **medium** — waves and their lanes with the justification, one line per task (id, lane, files, test-first or exemption, done).
- **fast** — one combined gate: Goal, Decisions and the tasks.
- **full** — `tasks.md` in full.

On change: small edits yourself; structural changes — relaunch the planner with the feedback. Gate again until approved.

## 3. Hand off

Router — return to it. Direct call — tell the user `/slimspec <slug>` continues with apply.
