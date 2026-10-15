---
name: verify
description: "Verify an applied slimspec change: reviewer agents check plan and design conformance, TDD evidence, deviations and code review, then findings are triaged. Use when the user runs /slimspec:verify or asks to review or check a slimspec change after apply."
argument-hint: "[change-slug]"
---

# verify

Input: `$ARGUMENTS` — change slug (ask which when several are active). Read `${CLAUDE_PLUGIN_ROOT}/skills/slimspec/protocol.md` first unless it is already loaded. Every task must be `- [x]`; otherwise run apply first.

## 1. Review

Depth: `review.depth` from config; `auto` → `fast` low, `medium` medium, `full` high.

Reviewer prompt: change folder path, `base:` sha, resolved test command, depth, focus. TDD evidence and deviations come from the `evidence:` / `deviations:` lines in the tasks, not from session reports, so a resumed session reviews the same way.

- **fast, medium** — one `slimspec:reviewer`, focus `all`.
- **full** — two `slimspec:reviewer` agents in one message: focus `spec` (spec conformance) and focus `code` (code review).

## 2. Triage

You triage; the reviewer's `kind` is a proposal. For each finding:

- **nit** — collect for the final summary; never triggers a cycle.
- **blocker / should-fix, implementation** (code misses what `explore.md` / `tasks.md` require, missing or wrong red evidence, files outside `files`, tautological test, bug) — reopen the owning task with `fix: <finding>` (delete its evidence lines); when no task owns it, add `F<n>` tasks in a new wave.
- **blocker / should-fix, design or intent** (the design is wrong or incomplete, the Goal is unreachable as designed, a deviation changes a decision) — show it to the user and run `refine`.

Show the report (step 3), then:

- Implementation findings only — if `fix-cycles` < 2: increment it, run apply, then verify again. If `fix-cycles` is 2: escalate via `AskUserQuestion` (one more fix cycle / refine / stop here), listing the findings still open.
- No blocker or should-fix left — verify passes. Return to the router (it runs ground) or, called directly, tell the user `/slimspec <slug>` continues with ground.

## 3. Report to the user

Build it from the reviewer YAML (in `full`, merge both reports); the YAML stays in the session. Samples: `${CLAUDE_PLUGIN_ROOT}/skills/verify/examples.md` — read before the first report.

- **Header** — `Verify · <slug> · round <n> ·` the counts per severity, or `pass`.
- **Summary table** — one row per check: suite, plan conformance, design conformance, TDD evidence, deviations, code review (skill or fallback, depth), skipped (from `skipped`, else `none`).
- **Findings** grouped Blockers / Should-fix / Nits, then Design / intent. Each: `file:line — issue`, `Fix:` the reviewer's recommendation, `→` its routing (reopen `T<n>`, new `F<n>`, or `refine`). Rewrite any vague recommendation into a concrete change before showing it.
- **Next** — the fix cycle (`<n>/2`), the refine question, the escalation, or ground.

## Guardrails

- Never fix code in this phase; fixes go through apply.
- Never drop a blocker or should-fix to pass verify; never start a fix cycle for nits.
- Design and intent findings always reach the user; never resolve them yourself.
- A skipped check is reported as skipped, never as passed.
