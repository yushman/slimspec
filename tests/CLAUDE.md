# tests

Fast dev-check tier: the plugin is well-formed as text. Never loaded or run by the plugin.

## Scope
- Owns static structure, artifact grammar and English-only prompts; never checks model behavior (that is `evals/`) or interaction wording (that is `/prompt-debate`).
- Runs with `python3 -m unittest discover -s tests`, stdlib only, in about a second; `.githooks/pre-commit` runs the whole suite before every commit.

## Checks
- Agents: frontmatter keys exactly `name`, `description`, `tools`, `model` in that order; `name` equals the filename; `model` equals the D16 tier in `DESIGN.md`.
- Skills: `plugin/skills/*/SKILL.md` frontmatter `name` equals the dir name and `description` is non-empty; the dir set equals the `skills/` list in the DESIGN Layout.
- Every `${CLAUDE_PLUGIN_ROOT}/…` path and relative markdown link in `plugin/skills/` and `plugin/agents/` resolves; refs containing `<` placeholders and URLs are skipped.
- Every `slimspec:<name>` in `plugin/skills/` names a skill dir or a `plugin/agents/<name>.md`.
- DESIGN `### Dn.` headings run sequentially from D1 and the last equals the `D1–Dn` range in root `CLAUDE.md`.
- No Cyrillic in `plugin/skills/`, `plugin/agents/`, `DESIGN.md`, `CLAUDE.md`.
- Every ```` ```markdown ```` block in `plugin/skills/*/examples.md` that carries artifact grammar passes it; other blocks are skipped.
- `evals/` runner, verdict, helpers and each case's `check.py` are unit-tested here against stub hosts and temp sandboxes, without calling a model.

## Modules
- `plugin.py` — the structure checks above, each returning a list of problem strings (empty when valid).
- `grammar.py` — the single parser of `explore.md` and `tasks.md` per `plugin/skills/slimspec/explore-template.md` and `tasks-template.md`: `parse_explore(text)`, `parse_tasks(text, kind)` (`full`, `section`, `lines`) and `check_markdown(text)` return problem lists with line numbers. `evals/` imports it instead of parsing again.
