# slimspec

[Русская версия](README.ru.md)

Lightweight spec-driven development for Claude Code: explore → plan → apply → verify → ground,
with mandatory red-green TDD and specs that live next to the code as module `CLAUDE.md` files.

Design and decisions: [DESIGN.md](DESIGN.md).

## Install

In Claude Code:

```
/plugin marketplace add yushman/slimspec
/plugin install slimspec@slimspec
```

Or load a local clone:

```bash
git clone https://github.com/yushman/slimspec ~/src/slimspec
claude --plugin-dir ~/src/slimspec
```

## Usage

```
/slimspec <idea>          # full cycle; mode from config, suggested after the scan
/slimspec                 # list active changes: resume or abandon one
/slimspec:fast <idea>     # start in a fixed mode, no mode suggestion
/slimspec:medium <idea>
/slimspec:full <idea>
```

Phase commands, each usable on its own: `/slimspec:explore`, `/slimspec:plan`, `/slimspec:apply`,
`/slimspec:verify`, `/slimspec:refine`, `/slimspec:ground`. `/slimspec <slug>` resumes a change
from its files in `.slimspec/changes/<slug>/`. Change folders are temporary: slimspec adds
`.slimspec/changes/` to `.gitignore` and deletes the folder after ground.

You stop twice: after explore (design) and after plan. Apply → verify → ground then run on their own;
you are asked again only for agent questions, design findings from verify, or after two
automatic fix cycles.

## Modes

| Phase   | fast                                   | medium                          | full                                          |
|---------|----------------------------------------|---------------------------------|-----------------------------------------------|
| explore | inline, ≤3 questions, merged with plan | scanner + grilling              | same + explicit gate on `explore.md`          |
| plan    | section inside `explore.md`            | planner agent, waves            | same + full `tasks.md` at the gate            |
| apply   | one implementer, TDD                   | parallel waves                  | same                                          |
| verify  | reviewer, depth `low`                  | reviewer, depth `medium`        | reviewer, depth `high`                        |
| ground  | update touched specs                   | distill + intent check          | same                                          |

TDD is enforced by red/green evidence in every mode; there is no TDD hook. Implementers run only their
task's tests; the full suite runs once after each wave and once more in verify.

## Migrating

```
/slimspec:migrate-openspec     # openspec/specs/ → module specs
/slimspec:migrate-superpowers  # Superpowers design docs → module specs
```

Specs only: each source spec is mapped onto modules, distilled into the configured `spec.format` and
checked against the code. You approve a source → spec table first and decide on every statement the
code disagrees with. Changes, plans and tooling are not converted; they are deleted only at a final
cleanup question. Code is never touched. Superpowers itself you uninstall with `/plugin uninstall`.

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

Run `/slimspec:init` for an interactive setup, or directly from the project root:

```bash
bash "<plugin dir>/scripts/init.sh"
```

Default models: scanner — sonnet, planner — opus, implementer — sonnet, reviewer — opus, grounder — opus.
slimspec never pushes.
