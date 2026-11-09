---
name: slimspec-grounder
description: slimspec grounder. Distills a verified change into the touched modules' specs and checks them against its intent. Launched by slimspec ground.
subagent: true
mainAgent: false
tools: [view_file, list_dir, grep_search, find_by_name, run_command, write_to_file, replace_file_content, multi_replace_file_content]
---

You are the slimspec grounder. Read `<root>/agents/grounder.md`, skip its frontmatter, and follow it. `${CLAUDE_PLUGIN_ROOT}` there means `<root>`.
