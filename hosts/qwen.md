# slimspec on Qwen Code

Mapping of the Claude Code terms used in slimspec files. `<root>` is the slimspec install root named in the stub skill. Wherever slimspec files say `${CLAUDE_PLUGIN_ROOT}`, use `<root>`.

## Questions

- `AskUserQuestion` maps to the `ask_user_question` tool. If it is missing or errors, ask a text question instead: one decision, 2-4 numbered options, the recommended option first and marked as recommended. Then end your turn and wait for the answer. Never pick a default and continue.
- Independent questions may be batched: up to 4 independent questions in one turn, each numbered with its own 2-4 options and recommendation, then end the turn.
- If `ask_user_question` errors or rejects the options, ask in text, end the turn, never pick a default and continue.

## Subagents

An Agent launch of `slimspec:<role>` (`subagent_type: slimspec:<role>`) means calling the `agent` tool with `subagent_type: slimspec-<role>` (defined in `~/.qwen/agents/` or `.qwen/agents/`). Roles: scanner, debugger, planner, implementer, reviewer, grounder. Scanner and reviewer have `write_file` and `edit` disallowed.

## Skills and commands

- `/slimspec:<phase>` and `/slimspec:<mode>` (for example `/slimspec:verify`, `/slimspec:fast`) mean `slimspec <phase|mode> <args>`: call that skill directly, reading `<root>/skills/<phase|mode>/SKILL.md` and following it with the arguments.
- The `/code-review` skill is unavailable. The reviewer runs its own fallback review pass instead.

## Models

Ignore model aliases such as `sonnet` and `opus`. Pass `models.<role>` from the config at spawn time only where this host supports a per-spawn model; otherwise the subagent inherits the session's model.

## Spec format

With no `spec.format` in `.slimspec/config.yaml`, the default is `agents-md` (specs live in `<unit>/AGENTS.md` and a root `AGENTS.md`), not `claude-md`. When `init` asks for the spec format, it lists `agents-md` first as recommended: options `agents-md` (recommended) | `claude-md` | `readme` | `central`, and the question text names `native` and `none`, which are reachable through a free answer.

## Unavailable

`migrate-openspec` and `migrate-superpowers` are unavailable on this host (Claude Code only). Say so and stop if asked.
