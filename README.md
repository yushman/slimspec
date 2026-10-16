# slimspec

Website: https://yushman.github.io/slimspec/

[Русская версия](README.ru.md)

## Spec-driven development plugin for Claude Code

slimspec is a Claude Code plugin. It runs the explore → plan → apply → verify loop with mandatory red-green TDD. A change uses two temporary files. Each module has one compact spec in a nested `CLAUDE.md`, which Claude Code loads automatically. The spec records where to look and what must not break; the model reads the code for everything else.

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

## A real migration

One existing project, a Rust + web log viewer, was moved from OpenSpec with `/slimspec:migrate-openspec`. Before and after:

|                       | OpenSpec                                    | slimspec                    |
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

The numbers come from one project; no benchmark was run. Results depend on how the source specs were written.

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

A change lives in `.slimspec/changes/<slug>/` as `explore.md` and `tasks.md`. The folder is gitignored (slimspec adds `.slimspec/changes/` to `.gitignore`) and removed after ground; the history is your commits and the updated specs. `/slimspec <slug>` resumes a change from its files.

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

slimspec reuses parts of both. The table lists only the points where slimspec differs.

|                       | OpenSpec | Superpowers | slimspec |
|-----------------------|----------|-------------|----------|
| Flow                  | explore → propose → apply → verify → archive, a command per step; explore and verify are optional | brainstorming → worktree → plan → execute → finish branch; skills trigger on their own | one command runs explore → ground; you stop at two gates |
| Artifacts per change  | proposal, design, tasks, delta specs; the folder then moves to an archive in the repo | for a project: a dated design doc in `docs/superpowers/specs/` (committed) and a plan in `docs/superpowers/plans/`; small changes stay in chat | `explore.md` + `tasks.md`, gitignored, deleted after ground |
| Spec merge            | ADDED / MODIFIED / REMOVED sections applied to the main spec, requirement by requirement, at archive | no merge into a living spec; one design doc per project | the model merges into the module spec, rewrites contradictions, checks intent |
| Subagents             | no built-in subagent mechanism | a fresh subagent per task with a review after each, or inline execution | scanner, planner, implementers, reviewer, grounder; structured reports, questions bubble up |
| Explore               | `/opsx:explore`, an optional thinking partner before a proposal | brainstorming; once a project's design is approved, the next step is a plan | grilling: one decision per question, independent ones together; plan starts only after your gate |

**What slimspec does not have.** OpenSpec keeps scenarios as explicit test cases and a full history of every change next to the specs, and it works with 30+ AI tools. Superpowers has skills outside the spec flow (debugging, worktrees, code review and others) and supports many coding agents. slimspec works only with Claude Code and covers only the spec-driven loop.

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

Default models: sonnet for scanner and implementer, opus for planner, reviewer and grounder. slimspec never pushes.

---

[GitHub](https://github.com/yushman/slimspec) · [Design and decisions](DESIGN.md) · [MIT license](LICENSE)
