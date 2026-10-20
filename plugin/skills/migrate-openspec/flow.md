# slimspec migration flow (main session)

Shared by `/slimspec:migrate-openspec` and `/slimspec:migrate-superpowers`. The calling skill defines its source: where the specs are, how to read them, and the cleanup list. The only output is specs in the configured `spec.format`; migration never touches code, never creates `.slimspec/changes/`, and deletes nothing before the cleanup gate.

`${CLAUDE_PLUGIN_ROOT}` in a file you opened with Read stays literal: it means the plugin root, the directory that holds `skills/` and `agents/` (two levels above this file). Replace it with that absolute path in every agent prompt.

## 1. Config

Read `.slimspec/config.yaml` if it exists; missing keys take defaults: `spec.format: claude-md`, `spec.unit: auto`, `spec.adr: false`, `commit: none`, `models: {}`.

## 2. Detect

Glob the source specs the skill lists. None found, or `spec.format: none` — say in one line that no specs are generated and why, then go to step 7 if the cleanup list finds anything; otherwise stop.

## 3. Map

Launch a general-purpose agent (Agent tool, `model: sonnet`) with the prompt in [mapper-prompt.md](mapper-prompt.md), placeholders filled: source kind, the detected spec files, `spec.format`, `spec.unit`, the skill's source notes. Its report is YAML (format in the prompt).

- **DONE** — keep the mapping.
- **BLOCKED** — ask its `questions` via `AskUserQuestion`, relaunch with the answers.
- **FAILED** — show the one-line reason, ask how to proceed.

## 4. Mapping gate

Show one table and ask via `AskUserQuestion`: approve / change.

| Source | Target spec | Notes |
|---|---|---|
| source spec | spec file(s) for `spec.format` | `new` / `merge` |
| project context | root `CLAUDE.md` | only facts not already there |
| left out | — | why |

Then ask the `ambiguous` items batched, one question per item (its options, recommendation first), up to 4 per call. Re-gate after changes until approved. All questions: one decision per question, 2–4 concrete options.

## 5. Distill

Launch a general-purpose agent (`model: opus`, or `models.grounder` from config) with the prompt in [distiller-prompt.md](distiller-prompt.md), placeholders filled: the approved source → target list, `spec.format`, `spec.unit`, `spec.adr`, the skill's examples path. Handle the report as in step 3.

Its `gaps` are source statements it did not write because the code contradicts them or shows no trace of them. Ask per gap via `AskUserQuestion`: drop (the code is the truth) / write as stated (the code is wrong; fix it later). When any answer is "write", relaunch with those statements only.

## 6. Summary

```
## Migrate · <openspec | superpowers> · specs
- <spec file> — created / updated: <operations from the report>
- root CLAUDE.md — updated / unchanged
Gaps: <statement — dropped / written>, or none
Left out: <source — why>, or none
Commit: <sha> or none (commit: none)
```

Commit the spec edits when `commit` is not `none`, with a short imperative lowercase message. Never push.

## 7. Cleanup gate

A separate final step. List everything from the skill's cleanup list that exists, grouped, one line each — files and folders to delete, and the exact lines to remove from files that stay. Ask via `AskUserQuestion`: delete all / keep all / choose. Delete only what the user approved. History stays in git. Commit the deletion when `commit` is not `none`.

## Guardrails

- Never edit code, tests or build files; never write anything but specs (and, at cleanup, approved deletions).
- Never delete before step 7 and its explicit approval.
- Never answer an agent's questions yourself.
