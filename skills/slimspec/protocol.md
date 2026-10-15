# slimspec protocol (main session)

Shared by the router and every phase skill. `${CLAUDE_PLUGIN_ROOT}` in a file opened with Read stays literal: the plugin root (holds `skills/` and `agents/`), two levels above this file.

## Config

`.slimspec/config.yaml`, optional; missing keys take their defaults:

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
models: {}                # per-role overrides, e.g. {implementer: opus}
```

`test: auto` — resolve the full-suite command once from the project (package.json scripts, Makefile, gradle, cargo, go, pytest config).

## Change folder

`.slimspec/changes/<slug>/` (slug: kebab-case, 2–4 words of the title) holds `explore.md` and `tasks.md`; in `fast`, tasks are the `## Tasks` section of `explore.md` ("tasks" means either). A phase given no slug while several changes are active asks which. The mode is the `mode:` line of `explore.md`. Formats: [explore-template.md](explore-template.md), [tasks-template.md](tasks-template.md).

Next phase, from files only:

| File state | Next phase |
|---|---|
| no folder or no `explore.md` | explore |
| `explore.md`, no tasks | plan |
| any open task (`- [ ]`, incl. `invalidated:` / `fix:`) | apply |
| all tasks `- [x]` | verify, then ground |

## Agents

You are the only decision-maker; agents only execute and report. The change files are the persisted snapshot of your context (for resume and gates) and the handoff medium to agents. Write anything decided in conversation that an agent needs to the files first, then launch. Prompts carry paths and ids — change folder, mode, resolved test command, the phase's inputs — never inlined artifact content; they add only what is not yet in files (e.g. the finding behind a `fix:`).

Launch `slimspec:scanner | planner | implementer | reviewer | grounder` with the Agent tool (`subagent_type`; `model` from `models.<role>` when set). Each returns only a YAML report (`status: DONE | BLOCKED | FAILED`, `task`, `files`, `decisions`, `deviations`, `tdd`, `questions`, role fields) defined in its agent file. It stays in the session; the user never sees agent YAML, logs or diffs.

- **DONE** — keep the report (compact); continue.
- **BLOCKED** — ask its `questions`; relaunch the same agent with the original prompt plus the answers.
- **FAILED** — show the one-line reason; ask how to proceed.

## Commits

`none` (default) — never. `lane` — once per lane, after all its tasks are DONE, that lane's `files`. `wave` — once per wave, after its suite is green. Short imperative lowercase messages. Never push.

## Asking the user

Only via `AskUserQuestion`, never in plain text: one decision per question, 2–4 concrete options, your recommendation first. Never answer an agent's question yourself.
