---
name: explore
description: "Explore a change idea for slimspec: scan the project, grill the user one decision at a time, write `explore.md` (goal, non-goals, decisions, risks). Use for /slimspec:explore or to think a change through before any plan. Stops at the design."
argument-hint: "<idea | change-slug>"
---

# explore

Input: `$ARGUMENTS` — idea or slug (from the router, also the mode). Read `${CLAUDE_PLUGIN_ROOT}/skills/slimspec/protocol.md` unless loaded. Unsure how to phrase a question or handle an entry point → read `${CLAUDE_PLUGIN_ROOT}/skills/explore/examples.md`.

Explore writes only `explore.md` — no code, tests or tasks — and never starts the plan; a request to implement means: finish the design.

## Stance

- Every claim about the project cites the brief or `path:line`; where the brief is silent, read the code.
- When the user's premise conflicts with code or specs, show the evidence first; recheck your own recommendation against the code.
- Never present a guess as fact; what stays unknown goes to Risks.
- In questions, ASCII diagrams and `preview` (single-select only) only when options differ in structure (layouts, data flow, code shape); the step 3 walkthrough uses diagrams wherever structure, flow or state changes; never decorative.

## Entry points

- **Vague idea** — approaches by cost and reach; the first question fixes scope; nothing about an unchosen approach.
- **Specific problem** — trace the current flow, locate the problem, test the user's diagnosis against it; the first question picks the scope.
- **Comparing options** — the deciding context (brief, else one question), a table of options against constraints, your recommendation, the question.
- **Stuck mid-change** — the slug has an `explore.md`: skip steps 1 and 3; read it, the tasks, the stuck task and its code; grill only new decisions, then `refine`. Never rewrite an existing `explore.md`.

## 1. Scan

- **medium, full** — `slimspec:scanner` with the idea and `spec.format`; keep the brief for the planner.
- **fast** — inline: the module `CLAUDE.md` files and the few source files the idea touches.

Mode not pinned and no `explore.md` — suggest one and confirm: `fast` — one module, a handful of files, no open decisions; `medium` — several files or modules, real decisions; `full` — cross-module or public-contract change, data migration, security, or high cost of error.

## 2. Grill

One decision per question, options grounded in the brief, a one-line trade-off each. New branches from answers join the list. Whatever the code decides, answer yourself; ask only what the user must decide, never decide it for them. Show the open branches between questions; done when every branch affecting Goal, Non-goals or Decisions is resolved. **fast** — at most 3 questions; the rest goes to Risks.

## 3. Finalize

- **medium, full** — first present the walkthrough in chat (no file), detailed enough to approve without opening files:
  - goal and observable outcome
  - how it works now vs after, citing `path:line`
  - ASCII diagrams wherever structure, data flow, control flow or state changes (before/after when it helps)
  - each decision: why, rejected alternatives
  - touched modules, files, public contracts
  - non-goals, risks

  Then ask: finalize / keep exploring (open branches named); keep exploring → step 2. This is the `medium` explore gate.
- **fast** — no offer; plan holds the combined gate.

Create `.slimspec/changes/<slug>/` and make sure `.slimspec/changes/` is a line of the project's `.gitignore` (append; create the file if missing; never touch other lines). Write `explore.md` there from `${CLAUDE_PLUGIN_ROOT}/skills/slimspec/explore-template.md`; Decisions carry context, choice and rejected alternatives.

- **full** — show `explore.md` in full; ask to approve or name changes until approved.

## 4. Hand off

Router — return to it. Direct call — tell the user `/slimspec <slug>` continues with plan.
