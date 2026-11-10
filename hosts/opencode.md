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

Ignore model aliases such as `sonnet` and `opus`. The `task` tool has no per-spawn model: a subagent's model comes only from `model: <provider/model>` in the frontmatter of its agent file, so `models.<role>` in the config is not used on this host.

`init` model questions: list the models with `opencode models` (via bash); never invent ids. Per role, up to 4 options: the `model:` already in the installed `slimspec-<role>.md` if set, else for debugger, planner, reviewer and grounder the strongest listed model, for scanner and implementer a fast one, recommended first; then the session model and other listed models. The rest are reachable via Other. Write each answer as a `model: <provider/model>` line in the frontmatter of the installed pointer agent `slimspec-<role>.md`, in `.opencode/agents/` of the project if the files are there, else in `~/.config/opencode/agents/`. At step 7, list each target agent file path and its `model:` line under the YAML, and write them only when the user answers write. The session model removes the `model:` line. Do not write `models` to the config; end the final line by saying models were written to the agent files. Reinstalling overwrites these lines; rerun `init` to restore them. Uninstall still removes the files by name. When the pointer agents carry no `model:` line, offer to run `init` via `AskUserQuestion` before the first agent launch; if declined, run on the session model.

## Spec format

With no `spec.format` in `.slimspec/config.yaml`, the default is `agents-md` (specs live in `<unit>/AGENTS.md` and a root `AGENTS.md`), not `claude-md`. When `init` asks for the spec format, it lists `agents-md` first as recommended: options `agents-md` (recommended) | `claude-md` | `readme` | `central`, and the question text names `native` and `none`, which are reachable through a free answer.

## Unavailable

`migrate-openspec` and `migrate-superpowers` are unavailable on this host (Claude Code only). Say so and stop if asked.
