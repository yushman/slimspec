# SlimSpec — design

## Goal

A lightweight spec-driven development framework for Claude Code, shipped as a plugin of
skills and agent definitions only (no scripts). It keeps what works in OpenSpec
and Superpowers — an explore → plan → apply loop, specs as artifacts, mandatory red-green
TDD — and drops what slows them down: long multi-step flows, artifact sprawl,
keyword-based spec merging, brainstorming that always pushes toward a plan, and
unreliable subagents.

Success looks like:

- A small change goes from idea to grounded specs with two user gates (design, plan) and
  no manual phase juggling.
- The main session always knows every decision and every subagent outcome, without its
  context filling up with logs and diffs.
- Specs live next to the code as module `CLAUDE.md` files, so Claude Code loads them
  automatically, and they stay current because grounding runs at the end of every change.

## Non-goals

- Support for agents other than Claude Code.
- A CLI, daemon, hooks or scripts.
- Persistent change history inside the repo (commits and grounded specs are the history).
- Up-front spec generation for a whole project.

## Flow

```
explore ──gate──▶ plan ──gate──▶ apply ──▶ verify ──▶ ground
   ▲                               ▲ │        │
   └──────────── refine ◀──────────┴─┴────────┘
```

| Phase  | fast                           | medium                        | full                                       |
|--------|--------------------------------|-------------------------------|--------------------------------------------|
| explore| inline, ≤3 questions, merged with plan | scanner + grilling     | same + explicit gate on explore.md         |
| plan   | section inside explore.md      | planner agent, waves of lanes | same + gate                                |
| apply  | one implementer, TDD           | waves, one implementer per lane | same                                     |
| verify | reviewer, review depth `low`   | reviewer, review depth `medium` | reviewer, review depth `high`            |
| ground | update touched specs           | distill + intent check        | same                                       |

Medium gates: after explore and after plan, each opening with a detailed walkthrough (D22). Apply → verify → ground then run without
stopping, except for escalations. `fast` has one combined gate on design and tasks. `full` adds
an explicit gate on the written `explore.md` and shows the whole `tasks.md` at the plan gate.

## Decisions

### D1. Claude Code only, packaged as a plugin
- **Context:** portability would require abstracting subagents and questions.
- **Choice:** Claude Code plugin with `skills/` and `agents/`.
- **Rejected:** multi-agent support (Codex, Cursor) — much more complexity for the first version.

### D2. The main session is the single source of context
- **Context:** the user steers decisions; subagents start cold.
- **Choice:** the main session runs grilling, writes `explore.md`, triages verify findings
  and keeps every subagent result. Subagents only execute and report. The change files are the
  persisted snapshot of the main session's context (resume, gates) and the handoff medium: prompts
  carry paths and task ids, never inlined artifact content; whatever an agent needs from the
  conversation is written to the files first, and a prompt adds only what is not yet there.
- **Rejected:** a subagent that owns explore — cleaner context, but grilling splits into
  rounds and the main session loses the reasoning.

### D3. Subagents never ask the user directly
- **Context:** subagents have no `AskUserQuestion`.
- **Choice:** a subagent that hits an open question stops with `status: BLOCKED` and a
  `questions:` block. The main session asks via `AskUserQuestion` and relaunches the
  subagent with the answers.

### D4. Structured subagent report
Every subagent returns only:

```yaml
status: DONE | BLOCKED | FAILED
task: T3
files: [src/auth/token.ts, src/auth/token.test.ts]
decisions: ["used existing clock abstraction"]
deviations: ["renamed validate → verifyToken"]
tdd:
  red: "token.test.ts: rejects expired token — FAIL (expected 401, got 200)"
  green: "12 passed"
questions: []
```

No raw logs or diffs. Details stay recoverable from the working tree. Role payloads ride in
extra fields: scanner `brief`, reviewer `findings` (each with a concrete `recommendation`),
`code_review` and `skipped` (checks skipped for a missing input), grounder `gaps`. An
implementer returns one report per task of its lane (`fast`: of the change).
- **Rejected:** full reports (context bloat); report files on disk (one more artifact type).

### D5. Implementer deviation policy
Minor deviations (names, signatures, an extra helper) are allowed and must be listed in
`deviations`. Anything that contradicts a decision in `explore.md`, or touches files outside
the task's `files`, is `BLOCKED`.

### D6. Explore never starts planning on its own
- **Context:** Superpowers' brainstorming always tries to produce a plan.
- **Choice:** a scanner subagent first studies the project (module `CLAUDE.md` specs, then
  code) and returns a compact brief. The main session then grills the user, one decision
  per question, via `AskUserQuestion` only: independent questions go together in one call (up
  to 4), dependent ones after their answer. When no open branches remain, it offers to
  finalize `explore.md`; the user decides. Plan starts only after the gate.

### D7. Plan is written by a planner subagent and is parallel-aware
The planner gets `explore.md` and the scanner brief, reads code, and writes `tasks.md`
grouped into waves, each split into lanes of cohesive tasks (same module or feature thread).
Lanes of one wave have disjoint `files`; tasks inside a lane may share files and run in listed
order; waves exist only for dependencies across lanes. Apply runs one implementer per lane, all
lanes of a wave at once, at most `apply.agents` (default 3); the planner never makes more lanes
per wave, merging lanes or splitting the wave instead. The planner justifies each wave's lanes,
which the plan gate shows. Parallelism uses disjoint files in the same working tree in every mode.
- **Rejected:** worktree isolation in `full` — subagent worktrees branch from committed state,
  so they miss uncommitted earlier waves unless every wave is committed; one implementer per
  task — repeated cold starts, each re-reading `explore.md`, specs and code; one implementer per
  wave — loses parallelism; lanes grouped by the main session at apply — invisible at the gate.

### D8. TDD is enforced by evidence, not tooling
Each task names its first failing test. The implementer must report a red run before
implementation and a green run after, running only the task's own tests. The main session runs the
full suite once after each wave (red → FAILED handling, culprit task named from the wave's reports);
the reviewer reruns it once in verify. Apply persists that evidence (and any deviations) as
one-line entries under the task in `tasks.md`, so verify works the same after a resume. Verify
rejects done tasks without red evidence. Tasks
where TDD does not apply (config, styles, migrations, docs) carry
`test: none — <reason>` plus an alternative check (build, lint, manual step); exemptions
are visible at the plan gate.
- **Rejected:** a `PreToolUse` hook that blocks production edits without a failing test — a
  prompt hook cannot verify a red run, and plugin hooks are always on, not per mode.

### D9. Verify findings are triaged in the main session
Reviewer findings come back to the main session:
- implementation bugs → sent back to apply automatically;
- design or intent issues → to the user via `refine`.

After two automatic fix cycles, the main session escalates to the user.

### D10. `refine` instead of re-running explore
`refine` patches `explore.md` and `tasks.md` from verify findings, an apply task BLOCKED or FAILED
because the design or plan is wrong, or new user input, marks
affected tasks `invalidated`, and sends only those back to apply. Approval resets `fix-cycles`.

### D11. Specs are nested module `CLAUDE.md` files
- **Choice:** Claude Code auto-loads nested `CLAUDE.md` files when working inside a
  directory, so specs reach the agent's context without extra steps.
- **Rejected:** `AGENTS.md` (not auto-loaded natively; symlinks or `@import` add noise);
  colocated `README.md` (not auto-loaded); a central `specs/` folder (detached from code).
- Other formats remain configurable (see Config).

### D12. Grounding: distill, AI-merge, check intent
1. Extract only durable knowledge from `explore.md` and the diff: behavior, invariants,
   contracts, decisions. Plans and process are dropped.
2. Merge into the module spec with the model, not by keywords: contradicting statements are
   rewritten, not appended.
3. Check that the updated specs cover the Goal and agree with the Decisions.
4. Delete only `.slimspec/changes/<slug>/`; `.slimspec/`, its config and `changes/` stay. It never reached git (D13): the history is the commits and
   the grounded specs.

Scope: only modules touched by the diff. The root `CLAUDE.md` is updated only for
cross-module decisions. Missing module specs are created lazily here — there is no init step.

### D13. Several active changes, one folder per slug
`.slimspec/changes/<slug>/` holds `explore.md` and `tasks.md`. These are temporary: explore adds
`.slimspec/changes/` to `.gitignore` when it creates the first folder (`.slimspec/config.yaml` stays
tracked), so commits under `commit: lane | wave` never include change artifacts. `/slimspec` without
arguments lists active changes to resume or abandon (delete the folder after confirmation, no ground).

### D14. Git behavior is configurable
`commit: none | lane | wave`, default `none`. The main session commits, never the agents; ground
commits spec edits when `commit` is not `none`. The framework never pushes.
- **Rejected:** a commit per task — tasks of one lane may share files and report together, so per-task commits cannot be exact.

### D15. Entry points and mode selection
`/slimspec <idea>` drives the whole cycle and resumes from file state. The router's full name is
`/slimspec:slimspec`; bare `/slimspec` works while no other command takes that name. Phase commands
(`/slimspec:explore`, `:plan`, `:apply`, `:verify`, `:refine`, `:ground`) are available
directly. `/slimspec:fast`, `/slimspec:medium` and `/slimspec:full <idea>` start the cycle
in a fixed mode and skip the mode suggestion. Plain `/slimspec` takes the mode from config;
after the scan, the router suggests a mode based on the size of the change and the user
confirms.

### D16. Model tier per role
scanner — sonnet, planner — opus, implementer — sonnet, reviewer — opus,
grounder — opus. Set in agent frontmatter and overridable in config.

### D17. `tasks.md` is semi-strict markdown
Fixed: the `base:` / `fix-cycles:` header lines, checkboxes, task ids, wave headings with their
lanes, the `invalidated:` / `fix:` markers, the `lane` / `files` / `test-first` (or `test: none`) /
`done` fields, and
the indented `evidence:` / `deviations:` lines under done tasks (reopening deletes them).
Everything else is free text. This is enough for the router to resume.
- **Rejected:** YAML blocks — easier to parse, harder to read at the plan gate.

### D18. `fast` still uses one implementer subagent
Keeps the main session free of test logs; same report contract as other modes.

### D19. Verify checklist
The reviewer reads the diff, `explore.md`, `tasks.md` (with its evidence lines) and the module
`CLAUDE.md` files of touched modules; surrounding code on demand. It reruns the whole test
suite itself and checks:

1. **Plan conformance** — every task closed, `done` criteria met, no files outside `files`.
2. **Design conformance** — Decisions respected, Non-goals untouched, Goal reached.
3. **TDD evidence** — a red run exists, it failed for the right reason (not a typo or a
   missing import), and the test checks behavior rather than a tautology.
4. **Deviations** — each listed deviation is acceptable under D5.
5. **Code review** — delegated to the built-in `/code-review` skill on the change diff;
   its findings are mapped onto the severities below. If the skill is unavailable to the
   subagent, the reviewer falls back to its own pass: correctness, project style, dead code,
   over-engineering, unrequested refactoring, basic security.

Review depth follows the mode — `fast` → `low`, `medium` → `medium`, `full` → `high` —
and is passed to `/code-review` as its effort level (the fallback pass scales the same way).
`review.depth` in config pins a fixed depth for every mode.

Severities: `blocker`, `should-fix`, `nit`. Blockers and should-fix items enter the fix
cycle (D9); nits are listed in the summary and never trigger a cycle.

### D20. Optional init in the session
- **Context:** config is optional, but its options are invisible until the user reads the docs.
- **Choice:** `/slimspec:init` asks via `AskUserQuestion` in two batched calls (D23) plus a confirm,
  writes `.slimspec/config.yaml`; it never runs on its own.
- **Rejected:** auto-creating config on first run (unrequested files); a bash wizard (skills can't
  drive an interactive script and `!` in the session has no TTY).

### D21. Migration from OpenSpec and Superpowers
- **Context:** projects that adopt SlimSpec often carry OpenSpec capability specs or Superpowers
  design docs; that knowledge should land in module specs, and the old files should not stay as a
  second source of truth.
- **Choice:** two user-invoked skills, `/slimspec:migrate-openspec` and
  `/slimspec:migrate-superpowers`, that only produce specs in the configured `spec.format`:
  - Specs only: OpenSpec `openspec/specs/*/spec.md` (plus `project.md` / `config.yaml` context for
    the root `CLAUDE.md`); Superpowers design docs count as its specs. Changes, plans and ledgers
    are never converted — they are only listed for cleanup. No source specs — nothing is generated.
  - Isolated: everything lives in the two skill folders. They run inline or launch general-purpose
    agents with prompts from their own folder, and only read `agents/grounder.md` for its merge
    rules and spec locations; core agents, skills and the change flow are untouched.
  - Flow: detect → map sources onto modules → mapping gate (source → spec table, ambiguities asked
    one by one) → distill with a code cross-check (a statement the code contradicts or does not
    show is asked about: drop / write as stated) → summary.
  - Cleanup after confirmation: a separate final step lists everything to delete (source specs,
    changes, plans, tooling, workflow lines in `CLAUDE.md`) and deletes only what the user approves.
    History stays in git. The Superpowers plugin is uninstalled by the user.
- **Rejected:** converting active changes and plans into `.slimspec/changes/` — needs new grammar,
  evidence markers and reviewer exceptions for work SlimSpec did not plan; switching to `central`
  specs to mirror OpenSpec's per-capability files — splits specs from code, against D11; extending
  the core agents and skills for migration — a one-off job would add permanent weight to every
  cycle; one combined skill — the two sources share no format.

### D22. Gates present a detailed walkthrough
- **Context:** a gate is where the user approves; a bare finalize question or one line per task
  forces the user to open files or approve blind.
- **Choice:** before each gate question the main session writes a walkthrough in chat (not a file
  — no new artifacts).
  - Explore: goal and observable outcome; how it works now vs after, citing `path:line`; ASCII
    diagrams wherever structure, data flow, control flow or state changes (before/after when it
    helps), never decorative; each decision with why and rejected alternatives; touched modules,
    files and public contracts; non-goals; risks.
  - Plan: totals (waves, lanes, tasks, exemptions); an ASCII diagram of waves → lanes → tasks with
    dependencies; per wave why it waits and why its lanes are independent; per task what changes
    and why, files, what the first failing test asserts, the done criterion; `test: none`
    exemptions listed separately with their check; what runs after approval (parallel lanes up to
    `apply.agents`, full suite per wave, review depth, commit policy, ground).
  - `fast`'s combined gate gets a condensed version of both. `full` additionally shows the written
    files in full, as before.
- **Rejected:** showing raw `explore.md` / `tasks.md` — written for agents and resume, terse, no
  diagrams or current-vs-new contrast; writing the walkthrough to a file — one more artifact per
  change.

### D23. Independent questions are asked together
- **Context:** one question per turn makes the user wait for a round trip per decision even when
  the set is known upfront.
- **Choice:** each question stays one decision with 2–4 options, recommendation first. Questions
  independent of each other's answers go together in one `AskUserQuestion` call (up to 4 per call;
  more means successive calls). A question whose options or relevance depend on another answer
  waits for it. Applies everywhere SlimSpec asks: explore grilling, agent `BLOCKED` questions,
  migration ambiguities.
- **Rejected:** strictly one question per turn — slow, no gain when answers are independent; one
  big question mixing decisions — unanswerable options.

## Artifacts

### explore.md

```markdown
# <change title>
mode: fast | medium | full
## Goal          — what changes and how we know it worked
## Non-goals
## Decisions     — ADR-lite: context / choice / rejected
## Risks
```

### tasks.md

```markdown
base: <sha at apply start>
fix-cycles: 0
## Wave 1 (lane A: src/auth/* · lane B: src/billing/*)
- [x] T1 · lane: A · files: src/auth/** · test-first: "rejects expired token" · done: 401 on expired
  evidence: red "rejects expired token — FAIL (expected 401, got 200)" · green "12 passed"
- [ ] T2 · lane: B · files: src/billing/** · test: none — config only · check: build
## Wave 2 (depends: T1 · lane A: src/api/*)
- [ ] T3 · invalidated: <reason> · lane: A · ...
- [ ] F1 · fix: <finding> · lane: A · ...
```

Markers: `invalidated:` (reopened by refine), `fix:` (reopened by verify), `F<n>` (fix task
added by verify when no task owns the finding).

## Config

`.slimspec/config.yaml`, optional; every key has a default.

```yaml
mode: medium              # fast | medium | full
spec:
  format: claude-md       # claude-md | readme | central | native | none
  unit: auto              # auto (by build files) | dir glob, e.g. "src/*/"
  adr: false              # also keep decisions in docs/adr/NNNN-*.md
test: auto                # or an explicit command
commit: none              # none | lane | wave
apply:
  agents: 3               # max parallel implementers = max lanes per wave
review:
  depth: auto             # auto (by mode) | low | medium | high
models: {}                # per-role overrides
```

Spec formats:
- `claude-md` — nested `CLAUDE.md` (default, auto-loaded);
- `readme` — colocated `README.md`;
- `central` — `specs/<capability>.md`, for features that cut across modules;
- `native` — language-native module docs (Go `doc.go`, Rust `//!`, Python package
  docstring, Kotlin `package-info`/KDoc);
- `none` — skip grounding.

`unit: auto` detects module boundaries from `package.json`, `go.mod`, `Cargo.toml`,
`build.gradle(.kts)`, `pyproject.toml`.

## Layout

```
slimspec/
  .claude-plugin/plugin.json
  skills/
    slimspec/   # router: config, mode, orchestration, resume
    fast/       # /slimspec:fast — router entry with mode pinned
    medium/
    full/
    explore/
    plan/
    apply/
    verify/
    refine/
    ground/
    init/       # /slimspec:init — interactive config setup
    migrate-openspec/     # /slimspec:migrate-openspec — shared migration flow and agent prompts
    migrate-superpowers/  # /slimspec:migrate-superpowers — source rules, uses the flow above
  agents/
    scanner.md
    planner.md
    implementer.md
    reviewer.md
    grounder.md
```
