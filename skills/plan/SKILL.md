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

Present the walkthrough in chat (no file), then ask via `AskUserQuestion`: approve / change. In every mode, list each `test: none` exemption separately, with its check.

- **medium** — the plan walkthrough:
  - totals: waves, lanes, tasks, exemptions
  - ASCII diagram of waves → lanes → tasks with dependencies
  - per wave: why it waits, why its lanes are independent
  - per task: what changes and why, files, what the first failing test asserts, done criterion
  - after approval: parallel lanes up to `apply.agents`, full suite per wave, review depth, commit policy, ground
- **fast** — one combined gate: condensed design (Goal, Decisions) and condensed plan walkthrough.
- **full** — the walkthrough plus `tasks.md` in full.

On change: small edits yourself; structural changes — relaunch the planner with the feedback. Gate again until approved.

## 3. Hand off

Router — return to it. Direct call — tell the user `/slimspec <slug>` continues with apply.
