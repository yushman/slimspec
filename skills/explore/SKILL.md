---
name: explore
description: "Explore a change idea for slimspec: scan the project, grill the user one decision at a time, and write `explore.md` (goal, non-goals, decisions, risks). Use when the user runs /slimspec:explore or wants to think a change through before any plan. Stops at the design; never writes tasks."
argument-hint: "<idea | change-slug>"
---

# explore

Input: `$ARGUMENTS` (when the router sent you here, it passes the idea and mode). Read `${CLAUDE_PLUGIN_ROOT}/skills/slimspec/protocol.md` first unless it is already loaded. Read `${CLAUDE_PLUGIN_ROOT}/skills/explore/examples.md` before your first question: sample entry points, diagrams and questions with previews.

Explore ends at a written `explore.md`. Planning starts only after the gate, and never from this skill.

## Stance

- **Ground in code** — every claim about the project cites the brief or `path:line`. When the brief does not cover something, read the code yourself.
- **Challenge assumptions, including your own** — when the user's premise conflicts with code or specs, show the evidence before asking anything. Recheck your own recommendation against the code before offering it.
- **Don't fake understanding** — read until you know, or say what is unknown. Never present a guess as fact; whatever stays unknown goes to Risks.
- **Visualize** — when a decision depends on structure (flow, states, data layout, timing), draw an ASCII diagram before the question.
- **Never write code** — no source, tests or tasks. The only file explore writes is `explore.md`. A request to implement means: finish the design; plan and apply do the work.

## Entry points

- **Vague idea** — after the scan, draw the solution space (approaches by cost and reach); the first question fixes scope. Ask nothing about an approach not yet chosen.
- **Specific problem** — trace the current flow from the brief and code, draw it, mark where the problem sits, and test the user's diagnosis against it. The first question picks what is in scope.
- **Comparing options** — get the context that decides it (from the brief, else one question); then a table of options against the constraints, your recommendation, and the question with a preview per option.
- **Stuck mid-change** — the slug names a change that already has `explore.md`: skip steps 1 and 3. Read `explore.md`, the tasks, the stuck task and its code; draw the conflict; grill only the new decisions; then run `refine` with the answers. Explore never rewrites an existing `explore.md`.

## 1. Scan

- **medium, full** — launch `slimspec:scanner` with the idea and `spec.format`. Keep its brief; the planner gets it later.
- **fast** — scan inline: read the module `CLAUDE.md` files and the few source files the idea touches. No agent.

If the mode is not pinned and no `explore.md` exists, suggest a mode from the brief (criteria in the router) and confirm it via `AskUserQuestion`.

## 2. Grill

Walk the decision tree with the user, one branch at a time, via `AskUserQuestion` only:

- Each question resolves one decision: concrete options grounded in the brief, your recommendation first, the trade-off in one line per option.
- When options differ in shape (data layout, flow, API, code), give each option a `preview` with an ASCII sketch or code snippet; previews work on single-select questions only.
- An answer may open new branches; add them. Answer from the code yourself whenever the code decides it — ask only what the user must decide.
- Keep a running list of open branches and show it between questions. Grilling is complete when every branch that affects Goal, Non-goals or Decisions is resolved.
- **fast** — at most 3 questions in total; record anything still open under Risks.

## 3. Finalize

- **medium, full** — offer to finalize via `AskUserQuestion` (finalize / keep exploring, with the remaining open branches named). The user decides; on "keep exploring" go back to step 2. This is the explore gate in `medium`.
- **fast** — skip the offer; the plan phase shows design and tasks in one gate.

Write `.slimspec/changes/<slug>/explore.md` from `${CLAUDE_PLUGIN_ROOT}/skills/slimspec/explore-template.md`, with the `mode:` line set. Decisions carry context, choice and rejected alternatives from the grilling.

- **full** — explicit gate on the written file: show `explore.md` in full and ask via `AskUserQuestion` to approve or name changes. Apply changes and ask again until approved.

## 4. Hand off

- Called by the router — return to it; it continues with plan.
- Called directly (`/slimspec:explore`) — stop. Tell the user: `/slimspec <slug>` continues with the plan.

## Guardrails

- One decision per question, always via `AskUserQuestion`; never ask in plain text, never bundle decisions.
- Never ask what the code answers; never decide for the user what only the user can decide.
- Never start a plan or write tasks; never write code.
- Never rewrite an existing `explore.md` — that is `refine`.
