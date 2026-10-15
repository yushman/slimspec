# explore.md template

Write `.slimspec/changes/<slug>/explore.md` in exactly this shape. Keep each section short; every line must be a decision-grade fact, not process notes. Before writing it, read the filled example in [examples.md](examples.md).

```markdown
# <change title>
mode: <fast | medium | full>

## Goal
<what changes, and how we know it worked — observable outcomes>

## Non-goals
- <what this change deliberately leaves alone>

## Decisions
### <decision title>
- **Context:** <why a choice was needed>
- **Choice:** <what we do>
- **Rejected:** <alternative — why not>

## Risks
- <risk — mitigation or "accepted">
```

`fast` only: append a `## Tasks` section that follows the grammar in `tasks-template.md` (one wave is typical).
