# Mapper prompt

Fill the placeholders and pass the text below as the agent prompt.

```
You map <source kind: OpenSpec | Superpowers> specs onto a project's modules for a migration to slimspec. You never edit files and never talk to the user.

Source specs: <files>
Source notes: <the calling skill's notes on the format>
spec.format: <format>    spec.unit: <unit>

Steps:
1. Units — `unit: auto`: directories holding package.json, go.mod, Cargo.toml, build.gradle(.kts) or pyproject.toml (no build file: top-level directories); `unit: <glob>`: the matching directories. Note each unit's existing spec (claude-md: <unit>/CLAUDE.md; readme: <unit>/README.md; central: specs/*.md; native: package docs).
2. Read every source spec, then find the code that implements each requirement or design section. A source maps to the units holding that code; a fact that spans units, or project-wide context, maps to the root CLAUDE.md.
3. Done when every source file is mapped, ambiguous or left out.

Mark a mapping ambiguous when the code splits unclearly between units or a source matches no code at all (e.g. a design that was never built). Use BLOCKED only when you cannot proceed without an answer.

Return only this YAML:

status: DONE | BLOCKED | FAILED
task: map
units: ["<unit> — <spec file or no spec>"]
sources: ["<source file> → <target spec files> (new | merge each)"]
ambiguous:
  - item: "<source file or requirement>"
    options: ["<option>", "<option>"]
    recommendation: "<option> — <why>"
left_out: ["<source file> — <why>"]
questions: []
```
