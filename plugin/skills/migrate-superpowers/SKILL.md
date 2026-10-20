---
name: migrate-superpowers
description: "Migrate Superpowers design docs into slimspec module specs, then delete Superpowers docs after confirmation."
argument-hint: "[docs dir]"
disable-model-invocation: true
---

# migrate-superpowers

Follow `${CLAUDE_PLUGIN_ROOT}/skills/migrate-openspec/flow.md` with the source below. Before the gate, read the filled example in `${CLAUDE_PLUGIN_ROOT}/skills/migrate-superpowers/examples.md`.

Input: `$ARGUMENTS` — a docs directory, when the user saved Superpowers docs somewhere else.

## Source specs

Superpowers design docs are its specs:

- current layout: `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`;
- older layout: `docs/plans/YYYY-MM-DD-<topic>-design.md`.

Designs are free-form: purpose, requirements, chosen approach and approaches considered, architecture, components, data flow, error handling, testing. Distill only what the code confirms; a later design overrides an earlier one on the same topic. A design whose code does not exist (never built) is ambiguous at the gate, recommended left out.

Implementation plans (`docs/superpowers/plans/*.md`, plans in `docs/plans/` titled `… Implementation Plan`) and progress ledgers (`.superpowers/sdd/`) are not migrated; they appear only in cleanup.

No design docs — no specs to generate: say so.

## Cleanup list

- Design docs and plans, in both layouts; `docs/superpowers/` once empty. In `docs/plans/` only Superpowers docs (`*-design.md`, `… Implementation Plan`), never other files.
- `.superpowers/` — git-ignored, so not in git history: say so at the gate.
- Hand-written lines in `CLAUDE.md` / `AGENTS.md` that reference Superpowers skills or docs — exact lines shown.

Never uninstall the plugin yourself. After cleanup, tell the user to run `/plugin uninstall superpowers@<marketplace>` — `claude-plugins-official` or `superpowers-marketplace`, whichever `/plugin` lists it under.
