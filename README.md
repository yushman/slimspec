# slimspec

Website: https://yushman.github.io/slimspec/

[Русская версия](README.ru.md)

## Strong models don't need heavy specs.

They read code fast. What they need is a short hint of where to look and what must not break. slimspec is a Claude Code plugin that keeps the explore → plan → apply → verify loop and mandatory red-green TDD, but drops the artifact sprawl: two temporary files per change, and one compact spec per module as a nested `CLAUDE.md` that Claude Code loads on its own.

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

This is one project, not a benchmark. Your numbers will depend on how your specs were written.

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

You stop twice: after explore and after plan. Each stop opens with a detailed walkthrough: the design with diagrams after explore, the full plan (waves, lanes, tests per task) after plan. The rest runs on its own and comes back to you only for agent questions, design findings, or after two automatic fix cycles.

The main session owns every decision. Subagents execute and return a short structured report (status, files, decisions, deviations, red/green evidence). They never ask you directly: an open question comes back as `BLOCKED`, the main session asks you and relaunches the agent with the answer.

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

slimspec borrows from both. The table covers only the parts slimspec does differently; why it changes them comes from the author's own use of both tools.

|                       | OpenSpec | Superpowers | slimspec |
|-----------------------|----------|-------------|----------|
| Flow                  | explore → propose → apply → verify → archive, a command per step; explore and verify are optional | brainstorming → worktree → plan → execute → finish branch; skills trigger on their own | one command runs explore → ground; you stop at two gates |
| Artifacts per change  | proposal, design, tasks, delta specs; the folder then moves to an archive in the repo | for a project: a dated design doc in `docs/superpowers/specs/` (committed) and a plan in `docs/superpowers/plans/`; small changes stay in chat | `explore.md` + `tasks.md`, gitignored, deleted after ground |
| Spec merge            | ADDED / MODIFIED / REMOVED sections applied to the main spec, requirement by requirement, at archive | no merge into a living spec; one design doc per project | the model merges into the module spec, rewrites contradictions, checks intent |
| Subagents             | no built-in subagent mechanism | a fresh subagent per task with a review after each, or inline execution | scanner, planner, implementers, reviewer, grounder; structured reports, questions bubble up |
| Explore               | `/opsx:explore`, an optional thinking partner before a proposal | brainstorming; once a project's design is approved, the next step is a plan | grilling: one decision per question, independent ones together; plan starts only after your gate |

**What they do better.** OpenSpec keeps scenarios as explicit test cases and a full history of every change next to the specs, and it works with 30+ AI tools. Superpowers covers far more ground: debugging, worktrees, code review and other skills beyond the spec flow, across many coding agents. slimspec works only with Claude Code and only does the spec-driven loop.

## Migrating from OpenSpec or Superpowers

```
/slimspec:migrate-openspec     # openspec/specs/ → module specs
/slimspec:migrate-superpowers  # Superpowers design docs → module specs
```

- Specs only. Each source spec is mapped onto modules, distilled into your `spec.format` and checked against the code.
- You approve a source → spec table first, and decide on every statement the code disagrees with.
- Changes, plans and tooling are not converted. They are deleted only at a final cleanup step, and only what you confirm. Code is never touched.
- The Superpowers plugin itself you remove with `/plugin uninstall`.

## Config

Optional. Without a config every key has a default. `/slimspec:init` tells you how to run a small wizard that asks one question per key and writes `.slimspec/config.yaml`:

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

Or run the wizard directly from the project root:

```bash
bash "<plugin dir>/scripts/init.sh"
```

Default models: scanner — sonnet, planner — opus, implementer — sonnet, reviewer — opus, grounder — opus. slimspec never pushes.

---

[GitHub](https://github.com/yushman/slimspec) · [Design and decisions](DESIGN.md) · [MIT license](LICENSE)
