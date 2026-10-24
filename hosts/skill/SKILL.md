---
name: slimspec
description: "Drive a slimspec change end to end (explore, plan, apply, verify, refine, ground, init), resuming from `.slimspec/changes/`. Use when the user says `slimspec <phase|mode> <args>`, asks to build a change with slimspec, or asks to resume or list slimspec changes."
---

# slimspec

The slimspec install root is `<root>`. It is the plugin root: wherever the slimspec files say `${CLAUDE_PLUGIN_ROOT}`, use `<root>`.

1. Identify your host by the tools you have. OpenCode has the `question` and `task` tools. Codex has subagent spawn tools and no `question` tool. ZCode has the `Task` subagent tool and no `question` tool. If unsure, pick the closest match by tools.
2. Read that host's mapping and follow it for the whole session: `<root>/hosts/opencode.md`, `<root>/hosts/codex.md` or `<root>/hosts/zcode.md`.
3. Look at the first argument after `slimspec`. If it names a phase or mode (`explore`, `plan`, `apply`, `verify`, `refine`, `ground`, `init`, `fast`, `medium`, `full`), read `<root>/skills/<it>/SKILL.md` and follow it with the rest of the arguments as its `$ARGUMENTS`. Otherwise (an idea, a change slug, or nothing) read `<root>/skills/slimspec/SKILL.md` and follow it with all the arguments as its `$ARGUMENTS`.
