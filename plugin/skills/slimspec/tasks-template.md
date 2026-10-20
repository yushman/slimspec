# tasks.md grammar

Semi-strict markdown: the router resumes from it, so the fixed parts are exact; everything else is free text.

```markdown
# Tasks: <change title>
base: <git sha at apply start, or "none">
fix-cycles: 0

## Wave 1 (lane A: src/auth/* · lane B: config/*)
<one line: why the lanes are independent and what ties each lane's tasks together>
- [x] T1 · lane: A · files: src/auth/token.ts, src/auth/token.test.ts · test-first: "rejects expired token" · done: 401 on expired token
  evidence: red "rejects expired token — FAIL (expected 401, got 200)" · green "4 passed"
  deviations: renamed validate → verifyToken
- [x] T2 · lane: B · files: config/billing.yaml · test: none — config only · check: build passes · done: flag readable at startup
  evidence: red n/a — config only · check "build passed"

## Wave 2 (depends: T1 · lane A: src/api/*)
- [ ] T3 · fix: no 401 check on refresh · lane: A · files: src/api/session.ts, src/api/session.test.ts · test-first: "refreshes token before expiry" · done: no 401 during refresh window
```

## Fixed parts

- **Header** — `base:`, `fix-cycles:`; the planner writes `none` and `0`.
- **Wave heading** — its lanes with their globs, `(lane A: <globs> · lane B: <globs>)`, prefixed `depends: <ids> · ` when it waits on earlier waves; one line under it justifies the lanes. At most `apply.agents` lanes per wave.
- **Lanes** — a lane groups cohesive tasks of one wave (same module or feature thread). Lanes of one wave have disjoint `files`; tasks inside a lane may share files and run in listed order. Waves exist only for dependencies across lanes.
- **Task line** — `- [ ] T<n>` (`F<n>` for fix tasks added by verify), fields joined by ` · `:
  - `lane:` — the task's lane in its wave: `A`, `B`, …
  - `files:` — every file the task may create or edit, tests included; paths or globs.
  - `test-first: "<first failing test>"`, or `test: none — <reason>` plus `check: <build | lint | manual step>`; `test: none` only for config, styles, migrations, docs.
  - `done:` — an observable criterion.
- **States** — `- [ ]` open, `- [x]` done (apply, after a DONE report). A reopened task is open with a marker right after its id: `invalidated: <reason>` (refine) or `fix: <finding>` (verify).
- **Evidence** — indented under every `- [x]` task, written by apply: `evidence: red "<test — failure>" · green "<result>"` (`test: none`: `red n/a — <reason> · check "<result>"`), and `deviations: <item>; <item>` when any. Redone tasks get fresh lines; reopening deletes them.

Free text never starts a line with `evidence:` or `deviations:`.

The planner reads [examples.md](examples.md) before writing tasks (a filled plan, reopened tasks, good vs bad task lines and lanes); everyone else only when unsure.
