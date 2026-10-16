# slimspec

Website: https://yushman.github.io/slimspec/

[Русская версия](README.ru.md)

## Strong models don't need heavy specs.

An agent rebuilds the picture by scanning the code, and it does that fast. A spec only has to tell it what to do and where to look. The explore step already is the spec of a change.

**slimspec** is a Claude Code plugin built on that. It runs the explore → plan → apply → verify loop with mandatory red-green TDD. A change uses two temporary files. Each module has one compact spec in a nested `CLAUDE.md`, which Claude Code loads automatically: where to look and what must not break, nothing else.

## Install

In Claude Code:

```
/plugin marketplace add yushman/slimspec
/plugin install slimspec@slimspec
```

Then: `/slimspec <idea>`

Or load a local clone:

```bash
git clone https://github.com/yushman/slimspec ~/src/slimspec
claude --plugin-dir ~/src/slimspec
```

## Measured on a real project

### Migration

One existing project, a Rust + web log viewer, was moved from OpenSpec with `/slimspec:migrate-openspec`. Before and after:

|                       | OpenSpec                                    | **slimspec**                    |
|-----------------------|---------------------------------------------|-----------------------------|
| Behavior specs        | 23 files, 2,941 lines, ~155 KB              | 3 files, 484 lines, ~34 KB  |
| Change archive        | 23 changes, 12,394 lines, ~733 KB           | 0                           |
| Root `CLAUDE.md`      | 130 lines                                   | 121 lines                   |
| Files in `openspec/`  | 200                                         | 0                           |

### Where the size went

- WHEN/THEN scenarios were folded into the requirements they describe. Empty Purpose sections and SHALL boilerplate are gone.
- One spec per module instead of 23 per feature. The agent reads only the spec of the module it works in: an edit in `web/` pulls ~11 KB, not a set of capability files scattered across the tree.
- The change archive is out of the working tree. It is still in that project's git history.

### What was lost

- Scenarios no longer exist as a list of test cases.
- Per-change rationale is gone. Part of it lives on in ADRs; the rest is only in git history.
- The largest module spec (~14 KB) is loaded whole for any work in that module.

Four **slimspec** changes later the module specs are 4 files and 641 lines, still 78% below the OpenSpec specs they replaced.

### Cost per change

The same project, before and after the migration, measured from Claude Code transcripts. Tokens are all input the model processed (input + cache read + cache write), main session and subagents together. The closest pair in size:

|                                  | OpenSpec (`logcat-padded-tags`) | **slimspec** full (`iana-tz-hash`) |
|----------------------------------|---------------------------------|--------------------------------|
| Code changed                     | 409 lines, 4 files, one module  | 435 lines, 15 files, three modules |
| Tokens processed                 | 45.7M                           | **29.7M (−35%)**               |
| Tokens per changed code line     | ~110k                           | **~68k (−38%)**                |
| Review                           | none                            | **2 verify rounds at depth high; one real blocker (panic on extreme dates) fixed inside the change** |
| Process files committed          | ~530 lines (proposal, design, tasks, delta specs, devlog) | **0** (change folder deleted; spec updates live in the module `CLAUDE.md` files) |
| Wall-clock span, gates included  | 91 min                          | 56 min                         |

The **slimspec** run also did more: 5 decision questions and 3 gates, 9 tasks in 3 waves, ground into 4 specs, an ADR and both READMEs.

Smaller changes point the same way. Two OpenSpec changes processed 31.5M and 45.7M tokens; two **slimspec** changes (fast and medium) 6.8M and 12.5M. One OpenSpec implementer alone processed 13–16M tokens; a **slimspec** subagent 0–1M, because each gets one narrow lane.

Caveats: n = 1–2 per flow, one project. The small **slimspec** changes were 5–10× smaller in code, so part of that gap is size. Some **slimspec** agents ran on Sonnet or Haiku. The **slimspec** full run's main session carried earlier unrelated context, which inflates its count.

## The flow

```
explore --gate--> plan --gate--> apply --> verify --> ground
   ^                              ^  ^        |
   |                              |  +-- fix -+   implementation bugs
   |                              |           |
   +-------- refine <-------------+-----------+   design issues
```

`refine` patches `explore.md` and sends invalidated tasks back to `apply`.

- `explore`: A scanner reads module specs, then code, and returns a short brief. The main session asks you questions (one decision per question, independent ones together) and writes `explore.md`. It never moves on to a plan by itself.
- `plan`: A planner writes `tasks.md` in waves and groups each wave into lanes of related tasks. Lanes in one wave touch disjoint files and run in parallel. Each task names its first failing test.
- `apply`: One implementer per lane works through its tasks in order, with red-green evidence for each. The full suite runs after each wave.
- `verify`: A reviewer checks plan and design conformance, TDD evidence and the code. Bugs go back to apply; design issues go to you through `refine`.
- `ground`: Durable knowledge (behavior, invariants, contracts, decisions) is distilled and merged into the touched module specs by the model, not by keywords. Then the change folder is deleted.

You stop twice: after explore and after plan. Each stop opens with a detailed walkthrough: the design with diagrams after explore, the full plan (waves, lanes, tests per task) after plan. The remaining phases run without stopping and return to you only for agent questions, design findings, or after two automatic fix cycles.

All decisions are made in the main session. Subagents execute and return a short structured report (status, files, decisions, deviations, red/green evidence). They never ask you directly: an open question comes back as `BLOCKED`, the main session asks you and relaunches the agent with the answer.

A change lives in `.slimspec/changes/<slug>/` as `explore.md` and `tasks.md`. The folder is gitignored (**slimspec** adds `.slimspec/changes/` to `.gitignore`) and removed after ground; the history is your commits and the updated specs. `/slimspec <slug>` resumes a change from its files.

TDD is enforced by red/green evidence in every mode; there is no TDD hook. Implementers run only their task's tests; the full suite runs once after each wave and once more in verify.

## Modes

| Phase     | fast                                   | medium                          | full                                          |
|-----------|----------------------------------------|---------------------------------|-----------------------------------------------|
| `explore` | inline, ≤3 questions, merged with plan | scanner + grilling              | same + explicit gate on `explore.md`          |
| `plan`    | section inside `explore.md`            | planner agent, waves of lanes   | same + full `tasks.md` at the gate            |
| `apply`   | one implementer, TDD                   | one implementer per lane        | same                                          |
| `verify`  | reviewer, depth `low`                  | reviewer, depth `medium`        | reviewer, depth `high`                        |
| `ground`  | update touched specs                   | distill + intent check          | same                                          |

The planner splits each wave into lanes of related tasks with disjoint files; apply runs one implementer per lane, up to `apply.agents` in parallel, each working through its tasks in order.

```
/slimspec <idea>          # mode from config, suggested after the scan
/slimspec:fast <idea>     # fixed mode, no suggestion
/slimspec:medium <idea>
/slimspec:full <idea>
/slimspec                 # list active changes: resume or abandon
```

Each phase is also a command of its own: `/slimspec:explore`, `/slimspec:plan`, `/slimspec:apply`, `/slimspec:verify`, `/slimspec:refine`, `/slimspec:ground`.

## Compared with OpenSpec and Superpowers

**slimspec** reuses parts of both. The table lists only the points where **slimspec** differs; the bold part of each **slimspec** cell is what it does better.

|                       | OpenSpec | Superpowers | **slimspec** |
|-----------------------|----------|-------------|----------|
| Flow                  | explore → propose → apply → verify → archive, a command per step; explore and verify are optional | brainstorming → worktree → plan → execute → finish branch; skills trigger on their own | **One command, two stops.** It runs explore → ground; you stop at two gates; verify is never skipped |
| Explore               | `/opsx:explore`, an optional thinking partner before a proposal | brainstorming; once a project's design is approved, the next step is a plan | **Explore is the spec of the change.** Grilling, one decision per question, writes `explore.md` (goal, non-goals, decisions, risks); no separate proposal or design |
| Artifacts per change  | proposal, design, tasks, delta specs; the folder then moves to an archive in the repo | for a project: a dated design doc in `docs/superpowers/specs/` (committed) and a plan in `docs/superpowers/plans/`; small changes stay in chat | **Nothing to commit but code and spec edits.** `explore.md` + `tasks.md`, gitignored, deleted after ground |
| Living spec           | one file per capability under `openspec/specs/`, read when you point the agent at it | none; one design doc per project | **Loaded on its own, only where you work.** One spec per module as a nested `CLAUDE.md` |
| Spec merge            | ADDED / MODIFIED / REMOVED sections applied to the main spec, requirement by requirement, at archive | no merge into a living spec | **Merged by meaning.** The model rewrites contradictions and checks the result against the change's intent |
| Subagents             | no built-in subagent mechanism | a fresh subagent per task with a review after each, or inline execution | **Narrow agents, cheap context.** Scanner, planner, parallel implementers per lane, reviewer, grounder, each on its own model; questions bubble up to you |
| Measured cost         | 45.7M tokens for a ~400-line change | not measured | **29.7M tokens for a comparable change, with two review rounds** |

**What slimspec does not have.** OpenSpec keeps scenarios as explicit test cases and a full history of every change next to the specs, and it works with 30+ AI tools. Superpowers has skills outside the spec flow (debugging, worktrees, code review and others) and supports many coding agents. **slimspec** works only with Claude Code and covers only the spec-driven loop.

## Migrating from OpenSpec or Superpowers

```
/slimspec:migrate-openspec     # openspec/specs/ → module specs
/slimspec:migrate-superpowers  # Superpowers design docs → module specs
```

- Specs only. Each source spec is mapped onto modules, distilled into your `spec.format` and checked against the code.
- You approve a source → spec table first, and decide on every statement the code disagrees with.
- Changes, plans and tooling are not converted. They are deleted only at a final cleanup step, and only what you confirm. Code is never touched.
- Remove the Superpowers plugin itself with `/plugin uninstall`.

## Config

Optional. Without a config every key has a default. `/slimspec:init` asks a few questions in the session and writes `.slimspec/config.yaml`:

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
models: {}                # per-role overrides: scanner, planner, implementer, reviewer, grounder
```

Default models: sonnet for scanner and implementer, opus for planner, reviewer and grounder. **slimspec** never pushes.

---

[GitHub](https://github.com/yushman/slimspec) · [Design and decisions](DESIGN.md) · [MIT license](LICENSE)
