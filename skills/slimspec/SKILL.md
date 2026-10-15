---
name: slimspec
description: "Drive a slimspec change end to end (explore, plan, apply, verify, ground), resuming from `.slimspec/changes/` state. Use when the user runs /slimspec, asks to build a change with slimspec, or asks to resume or list slimspec changes."
argument-hint: "[idea | change-slug]"
---

# slimspec router

Input: `$ARGUMENTS` — an idea, a change slug, or nothing. When an entry skill (`fast`, `medium`, `full`) sent you here, it pinned the mode and passed its own input.

Read `${CLAUDE_PLUGIN_ROOT}/skills/slimspec/protocol.md` first; it defines config, change folders, resume state, agent handling and commits. Every phase below means: read `${CLAUDE_PLUGIN_ROOT}/skills/<phase>/SKILL.md` and follow its steps for the current mode.

## 1. Resolve the change

- **No input** — list `.slimspec/changes/*/` with each change's title, mode and next phase (from the state table). Ask via `AskUserQuestion` which one to resume, or to start a new one (then ask for the idea).
- **Input matches an existing slug** — resume that change.
- **Otherwise** — the input is a new idea; the slug is chosen when `explore.md` is written.

## 2. Resolve the mode

First match wins:

1. Pinned by an entry skill — skip the mode suggestion.
2. The `mode:` line of an existing `explore.md`.
3. `mode` from config, then, after the scanner brief, the explore phase suggests a mode and the user confirms.

Mode suggestion, from the brief: `fast` — one module, a handful of files, no open design decisions; `medium` — several files or modules, real decisions to make; `full` — cross-module or public-contract change, data migration, security, or high cost of error.

## 3. Run the cycle

From the phase the state table gives, run in order:

```
explore ──gate──▶ plan ──gate──▶ apply ──▶ verify ──▶ ground
```

- **Gates** — the explore gate and the plan gate are the only planned stops (each phase skill defines its gate for the mode). After the plan gate, apply → verify → ground run without stopping.
- **Escalations** — stop and ask the user only for: a BLOCKED or FAILED agent report, design or intent findings from verify (→ `refine`), or a third fix cycle (see verify triage).
- **Verify loop** — verify returns either `pass` or findings. Implementation findings go back to apply automatically; then verify again. On `pass`, run ground.
- The cycle ends when ground closes the change.
