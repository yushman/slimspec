# tasks.md grammar

`tasks.md` is semi-strict markdown. The router resumes from it, so the fixed parts below are exact; everything else is free text.

```markdown
# Tasks: <change title>
base: <git sha at apply start, or "none">
fix-cycles: 0

## Wave 1 (parallel — disjoint files: src/auth/*, src/billing/*)
<one line: why these tasks are independent>
- [x] T1 · files: src/auth/token.ts, src/auth/token.test.ts · test-first: "rejects expired token" · done: 401 on expired token
  evidence: red "rejects expired token — FAIL (expected 401, got 200)" · green "12 passed"
  deviations: renamed validate → verifyToken
- [x] T2 · files: config/billing.yaml · test: none — config only · check: build passes · done: billing flag readable at startup
  evidence: red n/a — config only · check "build passed"

## Wave 2 (depends: T1)
- [ ] T3 · files: src/api/session.ts, src/api/session.test.ts · test-first: "refreshes token before expiry" · done: no 401 during refresh window
```

## Fixed parts

- **Header lines** `base:` and `fix-cycles:` — written by the router; the planner writes `base: none` and `fix-cycles: 0`.
- **Wave heading** `## Wave <n> (...)` — the parenthesis states `parallel — disjoint files: <globs>` or `depends: <task ids>`. Tasks in one wave have disjoint `files`.
- **Task line** starts with a checkbox and a task id: `- [ ] T<n>`; fix tasks added after verify use `F<n>`. Fields are separated by ` · `:
  - `files:` — every file the task may create or edit, tests included. Comma-separated paths or globs.
  - `test-first: "<name of the first failing test>"` — or `test: none — <reason>` plus `check: <build | lint | manual step>`. `test: none` is only for config, styles, migrations, docs.
  - `done:` — an observable completion criterion.
- **States:**
  - `- [ ]` open; `- [x]` done (set by the router after a DONE report).
  - `invalidated: <reason>` inserted after the id marks a task reopened by refine: `- [ ] T3 · invalidated: token TTL changed · files: ...`. Treat it as open.
  - `fix: <finding>` inserted after the id marks a task reopened by verify: `- [ ] T1 · fix: off-by-one in expiry check · files: ...`. Treat it as open.
- **Evidence lines** — indented under a done task, written by apply from the DONE report:
  - `evidence: red "<test — failure>" · green "<result>"`; for `test: none` tasks `evidence: red n/a — <reason> · check "<result>"`. Every `- [x]` task has one.
  - `deviations: <item>; <item>` — only when the report lists deviations.
  - Apply replaces both when the task is done again; reopening a task (`invalidated:`, `fix:`) deletes them.

Free text (wave justifications, notes under a task) is allowed anywhere else; never start a free-text line with `evidence:` or `deviations:`.

Before writing or patching tasks, read [examples.md](examples.md): a filled plan, the same plan with reopened tasks, and good vs bad task lines.
