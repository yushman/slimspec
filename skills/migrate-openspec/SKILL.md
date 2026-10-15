---
name: migrate-openspec
description: "Migrate OpenSpec capability specs into slimspec module specs, then delete OpenSpec files after confirmation."
disable-model-invocation: true
---

# migrate-openspec

Follow `${CLAUDE_PLUGIN_ROOT}/skills/migrate-openspec/flow.md` with the source below. Before the gate, read the filled example in `${CLAUDE_PLUGIN_ROOT}/skills/migrate-openspec/examples.md`.

## Source specs

- `openspec/specs/<capability>/spec.md` — `### Requirement:` blocks (`SHALL` statements) with `#### Scenario:` (WHEN / THEN). A placeholder `## Purpose` ("TBD …") carries nothing.
- Project context for the root `CLAUDE.md`: `openspec/project.md` and the `context:` text of `openspec/config.yaml`. `schema:` and `rules:` are process; dropped.
- Changes in `openspec/changes/` (active and `archive/`) are not migrated: archived ones are already in `specs/`, active ones are unbuilt. They appear only in cleanup.

No `openspec/specs/*/spec.md` and no project context — no specs to generate: say so.

## Cleanup list

- `openspec/` — specs, changes including `archive/`, `config.yaml`, `project.md`, `AGENTS.md`, `schemas/`. Name the active changes: their unbuilt work is dropped (it stays in git).
- `.claude/skills/openspec-*/`, `.claude/commands/opsx/`, legacy `.claude/commands/openspec/`; the same OpenSpec-generated skills and commands in other agents' folders at the repo root (`openspec-*`, `opsx*`).
- `<!-- OPENSPEC:START -->` … `<!-- OPENSPEC:END -->` blocks in root `CLAUDE.md` / `AGENTS.md`; a root `AGENTS.md` left empty goes too.
- Hand-written lines in `CLAUDE.md` / `AGENTS.md` that describe the OpenSpec workflow (`openspec/` paths, `/opsx:` commands) — exact lines shown.
