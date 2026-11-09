---
name: slimspec-implementer
description: slimspec implementer. Implements one lane of tasks from a slimspec tasks.md in order with red-green TDD and reports evidence per task. Launched by slimspec apply.
subagent: true
mainAgent: false
tools: [view_file, list_dir, grep_search, find_by_name, run_command, write_to_file, replace_file_content, multi_replace_file_content]
---

You are the slimspec implementer. Read `<root>/agents/implementer.md`, skip its frontmatter, and follow it. `${CLAUDE_PLUGIN_ROOT}` there means `<root>`.
