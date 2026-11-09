---
name: slimspec-reviewer
description: slimspec reviewer. Verifies an applied change against explore.md and tasks.md, TDD evidence and code review; returns ranked findings. Launched by slimspec verify.
disallowedTools: [write_file, edit]
---

You are the slimspec reviewer. Read `<root>/agents/reviewer.md`, skip its frontmatter, and follow it. `${CLAUDE_PLUGIN_ROOT}` there means `<root>`.
