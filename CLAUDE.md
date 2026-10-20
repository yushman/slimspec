# SlimSpec

Claude Code plugin: skills and agent definitions only, no scripts run by the plugin.

- Design and all decisions: `DESIGN.md` (decisions D1–D24). Follow them; change a decision there before changing behavior.
- Skill and agent prompts are in English.
- Dev tooling (`tests/`, `evals/`, `.githooks/`, `.claude/`) is never loaded or run by the plugin.
- Enable the pre-commit hook once per clone: `git config core.hooksPath .githooks`.
