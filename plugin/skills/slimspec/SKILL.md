---
name: slimspec
description: "Drive a slimspec change end to end (explore, plan, apply, verify, ground), resuming from `.slimspec/changes/` state. Use when the user runs /slimspec, asks to build a change with slimspec, or asks to resume or list slimspec changes."
argument-hint: "[idea | change-slug]"
---

# slimspec router

Input: `$ARGUMENTS` — an idea, a change slug, or nothing. An entry skill (`fast`, `medium`, `full`) that sent you here pinned the mode and passed its input; `debug` sends a slug with `explore.md` written.

Read `${CLAUDE_PLUGIN_ROOT}/skills/slimspec/protocol.md` first. Running a phase means: read `${CLAUDE_PLUGIN_ROOT}/skills/<phase>/SKILL.md` and follow it for the current mode.

## 1. Resolve the change

- **No input** — list `.slimspec/changes/*/` with title, mode and next phase. Ask: resume one, start a new one (then ask for the idea), or abandon one. Abandon: confirm via `AskUserQuestion`, delete that change folder (no ground), then list again.
- **An existing slug** — resume it.
- **Otherwise** — a new idea; explore picks the slug.

## 2. Resolve the mode

First match wins: pinned by an entry skill (no mode suggestion); the `mode:` line of an existing `explore.md`; config `mode`, after which explore suggests a mode for the user to confirm.

## 3. Run the cycle

From the phase the state table gives:

```
explore ──gate──▶ plan ──gate──▶ apply ──▶ verify ──▶ ground
```

- The explore and plan gates are the only planned stops; after the plan gate, apply → verify → ground run without stopping.
- Escalations stop the run: a BLOCKED or FAILED report (→ `refine` when the fix changes the design or plan), design or intent findings (→ `refine`), a third fix cycle.
- Verify findings for implementation go back to apply, then verify again; `pass` → ground, which closes the change.
