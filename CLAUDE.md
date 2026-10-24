# SlimSpec

Claude Code plugin: skills and agent definitions only, no scripts run by the plugin. The plugin lives in `plugin/` (`skills/`, `agents/`); `hosts/` (mapping files, stub skill, pointer agents) and `install.sh` serve OpenCode, Codex and ZCode; dev tooling at the repo root is not shipped.

- Design and all decisions: `DESIGN.md` (decisions D1–D28). Follow them; change a decision there before changing behavior.
- Skill and agent prompts are in English.
- Dev tooling (`tests/`, `evals/`, `.githooks/`, `.claude/`) is never loaded or run by the plugin.
- Enable the pre-commit hook once per clone: `git config core.hooksPath .githooks`.
