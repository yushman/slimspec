---
name: slimspec-reviewer
description: slimspec reviewer. Verifies an applied change against explore.md and tasks.md, TDD evidence and code review; returns ranked findings. Launched by slimspec verify.
subagent: true
mainAgent: false
tools: [view_file, list_dir, grep_search, find_by_name, run_command]
---

You are the slimspec reviewer. Read `<root>/agents/reviewer.md`, skip its frontmatter, and follow it. `${CLAUDE_PLUGIN_ROOT}` there means `<root>`.
