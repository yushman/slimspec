---
name: verify
description: "Verify an applied slimspec change: a reviewer checks plan, design, TDD evidence and code; findings are triaged. Use for /slimspec:verify or to review a slimspec change after apply."
argument-hint: "[change-slug]"
---

# verify

Input: `$ARGUMENTS` — change slug. Read `${CLAUDE_PLUGIN_ROOT}/skills/slimspec/protocol.md` unless loaded. Every task must be `- [x]`, else run apply. Never fix code here.

## 1. Review

Launch one `slimspec:reviewer`: change folder, `base:` sha, test command, depth — `review.depth`; `auto` → `fast` low, `medium` medium, `full` high.

## 2. Triage

The reviewer's `kind` is a proposal; you decide:

- **nit** — reported; never a cycle.
- **blocker / should-fix, implementation** (code misses explore or tasks, missing or wrong red evidence, files outside `files`, tautological test, bug) — reopen the owning task with `fix: <finding>`; no owner → `F<n>` tasks in a new wave, in lanes.
- **blocker / should-fix, design or intent** (design wrong or incomplete, Goal unreachable, a deviation changes a decision) — always to the user, then `refine`.

Never drop a blocker or should-fix to pass. After the report: implementation findings only and `fix-cycles` < 2 → increment, run apply, verify again; at 2 → ask: one more cycle / refine / stop, with the open findings. No blocker or should-fix → pass: return to the router, or tell the user `/slimspec <slug>` continues with ground.

## 3. Report

Samples: `${CLAUDE_PLUGIN_ROOT}/skills/verify/examples.md`. A skipped check shows as skipped, never as passed.

- **No findings** — one line: `Verify · <slug> · round <n> · pass · suite <result>` (+ `· skipped: <checks>`) `→ ground`.
- **Findings** — header `Verify · <slug> · round <n> ·` counts per severity (`pass` if only nits); a table, one row per check: suite, plan, design, TDD evidence, deviations, code review (skill or fallback, depth), skipped; findings grouped Blockers / Should-fix / Nits / Design-intent, each `file:line — issue`, `Fix:` a concrete change, `→` routing (reopen `T<n>`, new `F<n>`, `refine`); `Next:` fix cycle `<n>/2`, refine, escalation or ground.
