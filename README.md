# slimspec

[Русская версия](README.ru.md)

Lightweight spec-driven development for Claude Code: explore → plan → apply → verify → ground,
with mandatory red-green TDD and specs that live next to the code as module `CLAUDE.md` files.

Design and decisions: [DESIGN.md](DESIGN.md).

## Install

Clone the repo and load it as a plugin:

```bash
git clone <repo-url> ~/src/slimspec
claude --plugin-dir ~/src/slimspec
```

## Usage

```
/slimspec <idea>          # full cycle; mode from config, suggested after the scan
/slimspec                 # list active changes and resume one
/slimspec:fast <idea>     # start in a fixed mode, no mode suggestion
/slimspec:medium <idea>
/slimspec:full <idea>
```

Phase commands, each usable on its own: `/slimspec:explore`, `/slimspec:plan`, `/slimspec:apply`,
`/slimspec:verify`, `/slimspec:refine`, `/slimspec:ground`. `/slimspec <slug>` resumes a change
from its files in `.slimspec/changes/<slug>/`.

You stop twice: after explore (design) and after plan. Apply → verify → ground then run on their own;
you are asked again only for agent questions, design findings from verify, or after two
automatic fix cycles.

## Modes

| Phase   | fast                                   | medium                          | full                                          |
|---------|----------------------------------------|---------------------------------|-----------------------------------------------|
| explore | inline, ≤3 questions, merged with plan | scanner + grilling              | same + explicit gate on `explore.md`          |
| plan    | section inside `explore.md`            | planner agent, waves            | same + full `tasks.md` at the gate            |
| apply   | one implementer, TDD                   | parallel waves                  | same                                          |
| verify  | reviewer, depth `low`                  | reviewer, depth `medium`        | two reviewers (spec, code), depth `high`      |
| ground  | update touched specs                   | distill + intent check          | same + separate intent-check agent            |

TDD is enforced by red/green evidence in every mode; there is no TDD hook.

## Config

`.slimspec/config.yaml`, optional; every key has a default:

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
models: {}                # per-role overrides: scanner, planner, implementer, reviewer, grounder
```

Default models: scanner — sonnet, planner — opus, implementer — sonnet, reviewer — opus, grounder — opus.
slimspec never pushes.
