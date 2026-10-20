---
name: prompt-debate
description: Debate a diff of plugin/skills/, plugin/agents/ and DESIGN.md against the live-user interaction checklist. Use before committing prompt changes. Usage - /prompt-debate [ref]
---

Review whether a prompt diff weakens the rules of live-user interaction. Never edit prompts.

## 1. Diff

`ref` is the argument, default `HEAD`. Run `git diff <ref> -- plugin/skills/ plugin/agents/ DESIGN.md`. If it is empty, report an empty diff and stop.

## 2. Rounds

Items come from `${CLAUDE_SKILL_DIR}/checklist.md`. Round 1 covers all items; later rounds only items ruled `open`. At most 3 rounds.

Each round:
1. Launch `optimist` and `pessimist` in parallel (one message), giving each the diff command, the items and, after round 1, the arbiter's open points.
2. Launch `arbiter` with the diff command, the items and both replies.
3. Read its blocks: `Item N: safe | regression | open`, `Reason`, `Fix`, `Point`.

## 3. Open items

Items still `open` after round 3 go to the user via `AskUserQuestion`: one decision per question, 2-4 options, recommendation first, independent questions batched up to 4. Record the answers as the verdict.

## 4. Report

Prose only: a verdict per item (`safe`, `regression` with its fix, or the user's decision) and the agreed risks. No agent YAML, no raw diff.
