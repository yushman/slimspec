# slimspec on Codex

Mapping of the Claude Code terms used in slimspec files. `<root>` is the slimspec install root named in the stub skill. Wherever slimspec files say `${CLAUDE_PLUGIN_ROOT}`, use `<root>`.

## Questions

- `AskUserQuestion` has no tool on this host. Ask a text question instead: one decision, 2-4 numbered options, the recommended option first and marked as recommended. Then end your turn and wait for the answer. Never pick a default and continue.
- Independent questions may be batched: up to 4 independent questions in one turn, each numbered with its own 2-4 options and recommendation, then end the turn.
- The same rule applies if any question tool errors: ask in text, end the turn, never pick a default and continue.

## Subagents

An Agent launch of `slimspec:<role>` (`subagent_type: slimspec:<role>`) means spawning the Codex subagent `slimspec-<role>` (defined in `~/.codex/agents/` or `.codex/agents/`). Roles: scanner, debugger, planner, implementer, reviewer, grounder. Codex roles are not sandboxed per agent; read-only roles follow their instructions not to edit files.

## Skills and commands

- `/slimspec:<phase>` and `/slimspec:<mode>` (for example `/slimspec:verify`, `/slimspec:fast`) mean `slimspec <phase|mode> <args>`: call that skill directly, reading `<root>/skills/<phase|mode>/SKILL.md` and following it with the arguments.
- The Skill tool and the `/code-review` skill are unavailable. The reviewer runs its own fallback review pass instead.

## Models

Ignore model aliases such as `sonnet` and `opus`. Pass `models.<role>` from the config as the `model` of `spawn_agent`.

`init` model questions: the models are those listed under "Available models" in the `spawn_agent` tool description; never invent ids. Per role, up to 4 options: the existing `models.<role>` if set, else for debugger, planner, reviewer and grounder the strongest listed model, for scanner and implementer a fast one, recommended first; then the session model (writes no key for the role) and other listed models. The rest are reachable via Other. When `models` is empty or the config is missing, offer to run `init` via `AskUserQuestion` before the first agent launch; if declined, run on the session model.

## Spec format

With no `spec.format` in `.slimspec/config.yaml`, the default is `agents-md` (specs live in `<unit>/AGENTS.md` and a root `AGENTS.md`), not `claude-md`. When `init` asks for the spec format, it lists `agents-md` first as recommended: options `agents-md` (recommended) | `claude-md` | `readme` | `central`, and the question text names `native` and `none`, which are reachable through a free answer.

## Unavailable

`migrate-openspec` and `migrate-superpowers` are unavailable on this host (Claude Code only). Say so and stop if asked.
