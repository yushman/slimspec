# slimspec on OpenCode

Mapping of the Claude Code terms used in slimspec files. `<root>` is the slimspec install root named in the stub skill. Wherever slimspec files say `${CLAUDE_PLUGIN_ROOT}`, use `<root>`.

## Questions

- `AskUserQuestion` means the OpenCode `question` tool: one decision per question, 2-4 options, the recommended option first. Independent questions go together in one `question` call (up to 4 independent questions), each with its own options and recommendation.
- If the `question` tool errors or is unavailable, fall back to a text question: one decision, 2-4 numbered options, the recommended option first, then end your turn. Never pick a default and continue. Independent questions may be batched: up to 4 independent questions in one turn, each numbered with its own 2-4 options and recommendation, then end the turn.

## Subagents

An Agent launch of `slimspec:<role>` (`subagent_type: slimspec:<role>`) means spawning the native subagent `slimspec-<role>` with the OpenCode `task` tool. Roles: scanner, debugger, planner, implementer, reviewer, grounder.

## Skills and commands

- `/slimspec:<phase>` and `/slimspec:<mode>` (for example `/slimspec:verify`, `/slimspec:fast`) mean `slimspec <phase|mode> <args>`: call that skill directly, reading `<root>/skills/<phase|mode>/SKILL.md` and following it with the arguments.
- The Skill tool and the `/code-review` skill are unavailable. The reviewer runs its own fallback review pass instead.

## Models

Ignore model aliases such as `sonnet` and `opus`. Pass `models.<role>` from the config at spawn time only where this host supports a per-spawn model; otherwise the subagent inherits the session's model.

## Spec format

With no `spec.format` in `.slimspec/config.yaml`, the default is `agents-md` (specs live in `<unit>/AGENTS.md` and a root `AGENTS.md`), not `claude-md`. When `init` asks for the spec format, it lists `agents-md` first as recommended: options `agents-md` (recommended) | `claude-md` | `readme` | `central`, and the question text names `native` and `none`, which are reachable through a free answer.

## Unavailable

`migrate-openspec` and `migrate-superpowers` are unavailable on this host (Claude Code only). Say so and stop if asked.
