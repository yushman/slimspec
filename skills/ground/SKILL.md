---
name: ground
description: "Ground a verified slimspec change into module specs: distill durable knowledge into the touched modules' specs, check intent, delete the change folder. Use when the user runs /slimspec:ground or asks to update specs after a verified slimspec change."
argument-hint: "[change-slug]"
---

# ground

Input: `$ARGUMENTS` — change slug (ask which when several are active). Read `${CLAUDE_PLUGIN_ROOT}/skills/slimspec/protocol.md` first unless it is already loaded. Run only after verify passed.

## 1. Specs

`spec.format: none` — skip to step 2.

Grounder prompt: change folder path, `base:` sha, `spec.format`, `spec.unit`, `spec.adr`, and the changed files (from apply reports, else `git diff --name-only <base>` plus untracked files).

- **fast** — one `slimspec:grounder`, role `update` (distill and merge only).
- **medium** — one `slimspec:grounder`, role `ground` (distill, merge, intent check).
- **full** — `slimspec:grounder` role `update`; then a separate `slimspec:grounder` role `intent-check`. If it reports gaps, relaunch role `update` with the gaps once; gaps left after that go to the user via `AskUserQuestion`.

## 2. Close

- Commit the spec edits when `commit` is not `none`.
- Delete `.slimspec/changes/<slug>/`; git keeps the history.
- Show the ground summary (sample in `${CLAUDE_PLUGIN_ROOT}/skills/ground/examples.md`): header `Ground · <slug> · closed`; one line per spec file — created / updated / unchanged, with the operations from the grounder's `decisions`; the root `CLAUDE.md` line; intent check result (gaps closed or left); tests; nits left from verify; commit and folder deletion.

## Guardrails

- Never edit specs yourself; the grounder does. Never touch specs of modules outside the diff.
- Never delete the change folder before the grounder reports DONE and every gap is closed or answered by the user.
- Never commit when `commit` is `none`; never push.
