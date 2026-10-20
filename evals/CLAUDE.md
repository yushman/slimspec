# evals

Medium dev-check tier: headless runs of the plugin on a fixture repo, checking that following the prompts reaches the right files and phases. Never loaded or run by the plugin; run before a release.

## Runner
- `sh evals/run.sh [--case <name>] [--runs N]` (default 3 runs) runs each case N times and exits 1 if any case fails; a bad argument exits 2.
- Host command comes from `SLIMSPEC_EVAL_CMD`, default `claude -p --plugin-dir <repo root> --output-format stream-json --verbose --allowedTools Read,Glob,Grep,Write,Edit,Agent,Skill,Bash`; the prompt is its last argument and model pinning goes into the command. Non-Claude hosts load the plugin themselves.
- Each run gets a fresh `mktemp` sandbox: a copy of `fixture/` (a tiny Python `calc` package tested with `python3 -m unittest`) plus the case `seed/`, `git init` with one initial commit, and the host runs from there. `Bash` is not confined to the sandbox — accepted.
- Logs, `check.json` and the sandbox path of each run go to `evals/results/<timestamp>/<case>/<run>/`, which is git-ignored. No baseline or pass rate is recorded.

## Cases
- A case is `cases/<name>/{prompt.md, seed/, check.py}`. Headless has no live user, so every answer is stated in the prompt or seeded.
- `check.py <sandbox> <stdout log>` prints one JSON object of check name → `pass` | `fail` | `skipped`.
- Required checks read sandbox files, git state, the fixture test result and the last message. Trace checks (agent launches) run only when stdout parses as Claude stream-json, otherwise they are `skipped`.
- Cases: `fast-cycle` (`/slimspec:fast` adds `mul`: code and test green, `## Tasks` with red/green evidence, module spec updated, change folder deleted); `resume-routing` (a seeded approved explore leads to a valid `tasks.md` from the planner and no source change); `blocked-relaunch` (an ambiguous seeded task: the code reflects the prompt's answer; the implementer launches twice); `ground-scope` (only `calc/CLAUDE.md` and the change folder change, the folder is deleted, `.slimspec/config.yaml` stays).
- `fixture/` and `seed/` files, including `fixture/calc/CLAUDE.md`, are test data, not specs of this repo.

## Verdict
- `verdict.py` judges each check across runs: a `hard-*` check must pass in every run, any other in a majority; runs where it was `skipped` do not count, and a check skipped in all runs is `skipped`. A missing or invalid `check.json` counts as `hard-check-output: fail`.
- A case passes when no check fails; it prints `PASS|FAIL <case>` and one line per check; when no case ran it prints `no cases ran` and exits 1.

## Helpers
- `evallib.py` — trace parsing (`agent_launches`, `launched(text, agent, times)`, `tool_writes`, `last_message`), `changed_paths`, `fixture_tests_pass`, `report`, and `grammar()` loading `tests/grammar.py`.
