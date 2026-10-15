# slimspec protocol (main session)

Shared reference for the router and every phase skill. The main session is the single source of context: it talks to the user, writes `explore.md`, triages findings and keeps every agent report. Agents only execute and report.

`${CLAUDE_PLUGIN_ROOT}` in a slimspec file you opened with Read (not invoked as a skill) stays literal: it means the plugin root, the directory that holds `skills/` and `agents/` — two levels above this file.

## Config

Read `.slimspec/config.yaml` if it exists; every missing key takes its default:

```yaml
mode: medium              # fast | medium | full
spec:
  format: claude-md       # claude-md | readme | central | native | none
  unit: auto              # auto (by build files) | dir glob, e.g. "src/*/"
  adr: false              # also keep decisions in docs/adr/NNNN-*.md
test: auto                # or an explicit command
commit: none              # none | task | wave
review:
  depth: auto             # auto (by mode) | low | medium | high
models: {}                # per-role overrides, e.g. {implementer: opus}
```

- `test: auto` — resolve the full-suite command once from the project (package.json scripts, Makefile, gradle, cargo, go, pytest config) and pass the resolved command to every agent.
- `review.depth: auto` — `fast` → `low`, `medium` → `medium`, `full` → `high`.

## Change folder

- One folder per change: `.slimspec/changes/<slug>/` with `explore.md` and `tasks.md` (in `fast`, tasks live in the `## Tasks` section of `explore.md`).
- `<slug>` — kebab-case, 2–4 words from the change title.
- The mode of an existing change is the `mode:` line of its `explore.md`.
- Formats: [explore-template.md](explore-template.md), [tasks-template.md](tasks-template.md).

## State (resume)

Derive the next phase from files only:

| File state | Next phase |
|---|---|
| no folder, or no `explore.md` | explore |
| `explore.md`, no tasks (no `tasks.md`; in `fast` no `## Tasks`) | plan |
| any open task (`- [ ]`, incl. `invalidated` / `fix`) | apply |
| all tasks `- [x]` | verify (then ground) |

Done tasks carry their `evidence:` / `deviations:` lines (see the tasks grammar), so verify needs no reports from an earlier session.

## Running agents

Agents: `slimspec:scanner`, `slimspec:planner`, `slimspec:implementer`, `slimspec:reviewer`, `slimspec:grounder`. Launch each with the Agent tool, `subagent_type` set to that name. When `models.<role>` is set in config, pass it as the call's `model`.

Every prompt is self-contained (agents start cold): change folder path, mode, resolved test command, and the inputs the phase lists. Never paste file contents the agent can read itself.

Every agent returns only this report:

```yaml
status: DONE | BLOCKED | FAILED
task: T3
files: [...]
decisions: [...]
deviations: [...]
tdd: {red: "...", green: "..."}
questions: []
```

Role payloads ride in extra fields: scanner `brief`, reviewer `findings` and `code_review`, grounder `gaps`. The fast implementer returns a list of reports, one per task.

Handle it:

- **DONE** — keep the report (compact) for later phases; continue.
- **BLOCKED** — ask the `questions` via `AskUserQuestion`, then relaunch the same agent with the original prompt plus the answers. Agents never ask the user themselves.
- **FAILED** — show the user the one-line reason and ask how to proceed via `AskUserQuestion`.

Keep raw logs and diffs out of the session; details stay recoverable from the working tree.

## Commits

`commit: none` (default) — never commit. `task` — after each DONE implementer report, commit that task's `files` with a short imperative lowercase message. `wave` — commit once per finished wave. Never push.

## Asking the user

All questions to the user go through `AskUserQuestion`: one decision per question, 2–4 concrete options, your recommendation first.
