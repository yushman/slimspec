# prompt-debate

Slow dev-check tier: `/prompt-debate` judges whether a prompt diff weakens the rules of live-user interaction. Project-local, never shipped as a plugin skill.

## Scope
- Owns the wording of rules only a live user can observe: questions, gates, deciding for the user, BLOCKED, agent YAML in chat, escalation, DESIGN before behavior. Never structure (`tests/`) or outcomes (`evals/`).
- Runs in the main session, because open points must reach the user.

## /prompt-debate [ref]
- Reviews `git diff <ref> -- plugin/skills/ plugin/agents/ DESIGN.md`, `ref` defaulting to `HEAD`; an empty diff stops it.
- Items come from `checklist.md` (8 items: `AskUserQuestion`; question shape per D6, D23; explore asks instead of deciding; gates per D22; BLOCKED relaunch per D3; no agent YAML or diffs in chat per D4; escalation per D9; DESIGN before behavior).
- A round launches `optimist` and `pessimist` (sonnet) in parallel, each arguing per item with cited diff lines, then `arbiter` (opus), which rules each item `safe`, `regression` with a concrete fix, or `open` with the unresolved point.
- Round 1 covers all items, later rounds only `open` ones, at most 3 rounds; items still `open` go to the user via `AskUserQuestion`, one decision per question, 2-4 options, recommendation first, batched up to 4.
- The report is prose: a verdict per item and the agreed risks; no agent YAML, no raw diff.
- The skill and its agents are read-only (Bash for read commands) and never edit prompts or talk to the user.
