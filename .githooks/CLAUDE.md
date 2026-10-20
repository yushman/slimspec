# .githooks

Git hooks for this repo's dev checks. Never loaded or run by the plugin.

- `pre-commit` (POSIX sh) runs the whole fast tier (`python3 -m unittest discover -s tests`) from the repo root and blocks the commit on failure; `git commit --no-verify` bypasses it.
- Enabled once per clone with `git config core.hooksPath .githooks`.
