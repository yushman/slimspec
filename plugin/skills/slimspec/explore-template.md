# explore.md template

Write `.slimspec/changes/<slug>/explore.md` in exactly this shape: short sections, every line a decision-grade fact, no process notes. Unsure about the shape → see the filled example in [examples.md](examples.md).

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

`fast` only: append `## Tasks` in the grammar of `tasks-template.md` (usually one wave).
