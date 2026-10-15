---
name: refine
description: "Patch an in-progress slimspec change from verify findings or new input: update `explore.md` and `tasks.md`, reopen only affected tasks. Use for /slimspec:refine or when requirements of an active slimspec change shift mid-cycle."
argument-hint: "[change-slug] [what changed]"
---

# refine

Input: `$ARGUMENTS` — change slug and/or what changed; from the router, the design or intent findings. Read `${CLAUDE_PLUGIN_ROOT}/skills/slimspec/protocol.md` unless loaded. Refine patches the change; explore is never re-run.

1. **Resolve** what each finding or input changes (table below); when the user must choose, grill as in explore step 2.
2. **Patch `explore.md`** in place; a superseded statement is replaced, never left beside its replacement.
3. **Patch tasks** — reopen only the affected tasks with `invalidated: <reason>` (per the grammar) and adjust their fields; new tasks go in a new wave. Untouched tasks stay `- [x]`. Structural replanning in `medium` / `full`: relaunch `slimspec:planner` with the change notes.
4. **Confirm** — show the changes to both files and the reopened tasks; ask approve / change. Nothing goes to apply before approval; approval sets `fix-cycles: 0`.
5. **Hand off** — router: apply runs only the reopened tasks. Direct call: tell the user `/slimspec <slug>` continues with apply.

Worked example: `${CLAUDE_PLUGIN_ROOT}/skills/slimspec/examples.md`.

| Finding or input | `explore.md` | Tasks |
|---|---|---|
| Goal changed or unreachable as designed | Goal; Decisions that make it reachable | invalidate those delivering the changed part; new ones for new parts |
| Decision wrong or superseded | replace it; old choice → **Rejected** with reason | invalidate those implementing it |
| Missing decision | add it | adjust open tasks or add a wave |
| Deviation that changes a decision | accepted: rewrite the Decision to match the code | rejected: `invalidated: <deviation> rejected` |
| Scope grows | Goal (+ Decisions if a choice is needed) | new wave |
| Scope shrinks | Goal; dropped part → Non-goals | invalidate done tasks whose code must go |
| Non-goal touched, user keeps it out | — | invalidate the task that touched it |
| New risk or accepted trade-off | Risks: mitigation or "accepted" | none, unless the mitigation is work |
