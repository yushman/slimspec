---
name: init
description: "Interactive setup of .slimspec/config.yaml in the session."
disable-model-invocation: true
---

The config is optional: every key has a default. Ask with `AskUserQuestion`; each option gets a one-line description of its meaning.

1. If `.slimspec/config.yaml` exists, show it; its current values are the recommended (first) options below. Otherwise the defaults are.
2. Detect the test command by reading files: `package.json` with a `"test"` script -> `npm test`; `Makefile` with `test:` -> `make test`; `gradlew` -> `./gradlew test`; `Cargo.toml` -> `cargo test`; `go.mod` -> `go test ./...`; `pyproject.toml` or `pytest.ini` -> `pytest`. First match wins.
3. One call, 4 questions:
   - `mode`: fast | medium | full.
   - `spec.format`: claude-md | readme | central | native (4 options max; name `agents-md` and `none` in the question text, reachable via Other).
   - `test`: auto | the detected command, if any; an explicit command via Other.
   - `commit`: none | lane | wave.
4. One call:
   - `apply.agents` (max parallel implementers): 3 | 1 | 2 | 5; another integer >= 1 via Other.
   - `review.depth`: auto | low | medium | high.
   - Only when `spec.format` is not `none`: `spec.unit` (auto | a dir glob via Other, e.g. `src/*/`) and `spec.adr` (no | yes: also keep decisions in `docs/adr/`).
5. One call:
   - `changes.closed` (closed change folders): delete | archive (moved to `.slimspec/archive/<date>-<slug>/`).
   - `changes.gitignore`: yes (add change folders to `.gitignore`) | no (tracked; change files go into lane or wave commits).
6. Models, two calls: scanner, debugger, planner, then implementer, reviewer, grounder. Recommended (first) option per role: its existing `models.<role>`, else its D16 tier (heavy: debugger, planner, reviewer, grounder; light: scanner, implementer).
   - Claude Code: opus | sonnet | haiku; the default tier is the role's agent frontmatter model. Write only roles whose answer differs from it.
   - Other hosts: the options and how to list them come from the host mapping's Models section. Write every answer to `models`, except the session model, which writes no key, unless the mapping says otherwise.
7. Show the resulting YAML in the exact layout of the config block in [protocol.md](../slimspec/protocol.md) (same keys, aligned `#` comments; quote `spec.unit` and `test` unless `auto`), then ask: write | change. On change, re-ask only the keys the user names.
8. On write, create `.slimspec/` and write `.slimspec/config.yaml`. Never touch `.gitignore`. Reply with one line: the written path; models can be edited in the file.
