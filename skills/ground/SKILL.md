---
name: ground
description: "Ground a verified slimspec change: distill it into the touched modules' specs, check intent, delete the change folder. Use for /slimspec:ground or to update specs after a verified slimspec change."
argument-hint: "[change-slug]"
---

# ground

Input: `$ARGUMENTS` — change slug. Read `${CLAUDE_PLUGIN_ROOT}/skills/slimspec/protocol.md` unless loaded. Run only after verify passed. Never edit specs yourself.

## 1. Specs

`spec.format: none` — skip to step 2.

Launch one `slimspec:grounder` with the change folder, `base:` sha, `spec.format`, `spec.unit`, `spec.adr`, the changed files (from apply reports, else `git diff --name-only <base>` plus untracked files) and the role: `fast` — `update` (distill and merge); `medium`, `full` — `ground` (also the intent check). Gaps it reports go to the user via `AskUserQuestion`; relaunch it with role `update` and the answers when they need spec edits.

## 2. Close

Only after a DONE report with every gap closed or answered:

- Commit the spec edits when `commit` is not `none`.
- Delete only `.slimspec/changes/<slug>/`. `.slimspec/`, `config.yaml` and `changes/` stay, even when `changes/` is left empty.
- Summary (sample: `${CLAUDE_PLUGIN_ROOT}/skills/ground/examples.md`): `Ground · <slug> · closed · <commit | no commit> · deleted .slimspec/changes/<slug>/`, then one line per spec file — created / updated, with its operations from the grounder's `decisions`.
