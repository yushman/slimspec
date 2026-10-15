---
name: refine
description: "Patch an in-progress slimspec change from verify findings or new user input: update `explore.md` and `tasks.md`, invalidate only the affected tasks. Use when the user runs /slimspec:refine or changes requirements of an active slimspec change mid-cycle."
argument-hint: "[change-slug] [what changed]"
---

# refine

Input: `$ARGUMENTS` — change slug and/or what changed; when the router sent you here, it passes the design or intent findings. Read `${CLAUDE_PLUGIN_ROOT}/skills/slimspec/protocol.md` first unless it is already loaded.

Refine patches the existing change; explore is never re-run.

1. **Resolve** — for each finding or input, decide what it changes (table below). When the user must choose, grill as in explore step 2 (`AskUserQuestion`, one decision at a time).
2. **Patch `explore.md`** — rewrite the affected Goal, Non-goals, Decisions or Risks in place; a superseded decision is replaced, never left beside its replacement.
3. **Patch tasks** — for each task the change affects, insert `invalidated: <reason>` after its id, set it to `- [ ]`, delete its `evidence:` / `deviations:` lines, and adjust its fields. Add new tasks in a new wave (disjoint `files` within the wave). Structural replanning in `medium` / `full`: relaunch `slimspec:planner` with the change notes. Untouched tasks stay `- [x]`.
4. **Confirm** — show what changed in both files and the list of reopened tasks; ask via `AskUserQuestion`: approve / change. Set `fix-cycles: 0` on approval.
5. **Hand off** — router: continue with apply (only the reopened tasks run). Called directly: tell the user `/slimspec <slug>` continues with apply.

## Where each change lands

Worked example (thresholds raised mid-cycle): `${CLAUDE_PLUGIN_ROOT}/skills/slimspec/examples.md`.

| Finding or input | `explore.md` | Tasks |
|---|---|---|
| Goal unreachable as designed, or Goal changed | Goal; the Decisions that make it reachable | invalidate tasks delivering the changed part; new tasks for new parts |
| Decision wrong or superseded | Decisions: replace it; the old choice moves to **Rejected** with the reason | invalidate tasks that implement it |
| Missing decision (a gap the design never covered) | Decisions: add it | adjust open tasks or add tasks in a new wave |
| Deviation that changes a decision | accepted: Decisions rewritten to match the code | rejected: invalidate the task (`invalidated: <deviation> rejected`) |
| Scope grows (new requirement mid-cycle) | Goal, and Decisions if it needs a choice | new tasks in a new wave |
| Scope shrinks | Goal; the dropped part into Non-goals | invalidate done tasks whose code must go |
| Non-goal touched, and the user keeps it out | none | invalidate the task that touched it |
| New risk or accepted trade-off | Risks: mitigation or "accepted" | none, unless the mitigation is work |

## Guardrails

- Never leave a superseded statement beside its replacement.
- Reopen only affected tasks; never uncheck a task the change does not touch.
- Never send tasks back to apply before the user approves.
