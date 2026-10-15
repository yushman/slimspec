---
name: plan
description: "Turn an approved slimspec `explore.md` into `tasks.md`: TDD tasks grouped into parallel waves, then the plan gate. Use when the user runs /slimspec:plan or asks to plan an explored slimspec change."
argument-hint: "[change-slug]"
---

# plan

Input: `$ARGUMENTS` — change slug (when several changes are active and none is given, ask which). Read `${CLAUDE_PLUGIN_ROOT}/skills/slimspec/protocol.md` first unless it is already loaded. Requires `explore.md`; without it, run explore first.

## 1. Write the plan

- **medium, full** — launch `slimspec:planner` with: change folder path, the scanner brief (if this session has it), the resolved test command. It writes `tasks.md` following `${CLAUDE_PLUGIN_ROOT}/skills/slimspec/tasks-template.md`.
- **fast** — write the `## Tasks` section of `explore.md` yourself, same grammar, usually one wave. Each task names its first failing test or `test: none — <reason>` with a check. Read the good and bad task lines in `${CLAUDE_PLUGIN_ROOT}/skills/slimspec/examples.md` first.

## 2. Gate

Present the plan and ask via `AskUserQuestion`: approve / change.

- **medium** — summary: waves with their justification, one line per task (id, files, test-first or exemption, done), and every `test: none` exemption listed separately.
- **fast** — one combined gate: the design (Goal, Decisions) and the tasks together.
- **full** — show `tasks.md` in full, exemptions called out.

On "change": small edits — edit the file yourself; structural changes — relaunch the planner with the feedback. Gate again until approved.

## 3. Hand off

- Called by the router — return to it; it continues with apply.
- Called directly (`/slimspec:plan`) — stop. Tell the user: `/slimspec <slug>` continues with apply.

## Guardrails

- Never approve the plan for the user; the gate always goes through `AskUserQuestion`.
- Never hide a `test: none` exemption: every one is visible at the gate.
- Never answer a BLOCKED planner's questions yourself; they go to the user per protocol.
- No code in this phase.
