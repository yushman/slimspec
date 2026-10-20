import re

MODES = ("fast", "medium", "full")
SECTIONS = ("Goal", "Non-goals", "Decisions", "Risks")
WAVE_RE = re.compile(r"^#{2,3} Wave (\d+) \((.*)\)\s*$")
TASK_RE = re.compile(r"^- \[( |x)\] ([TF]\d+)\b(.*)$")
LANE_RE = re.compile(r"^lane ([A-Z]): \S")
EVIDENCE_RE = re.compile(r"^\s+(evidence|deviations): \S")


def _p(n, msg):
    return "line %d: %s" % (n, msg)


def _task_line(line, n):
    problems = []
    m = TASK_RE.match(line)
    parts = m.group(3).split(" · ")
    if parts[0].strip():
        problems.append(_p(n, "junk after task id"))
    fields = parts[1:]
    if fields and re.match(r"(invalidated|fix): \S", fields[0]):
        fields = fields[1:]
    names = []
    for f in fields:
        k = re.match(r"(lane|files|test-first|test|check|done): ", f)
        names.append(k.group(1) if k else None)
    if None in names:
        problems.append(_p(n, "unrecognised field %r" % fields[names.index(None)][:30]))
    order = ["lane", "files"]
    if "test" in names:
        order += ["test", "check"]
    else:
        order += ["test-first"]
    order += ["done"]
    for need in order:
        if need not in names:
            problems.append(_p(n, "task %s missing %s field" % (m.group(2), need)))
    if "test" in names and not fields[names.index("test")].startswith("test: none — "):
        problems.append(_p(n, "test field must be 'test: none — <reason>'"))
    if "test" in names and "test-first" in names:
        problems.append(_p(n, "both test-first and test: none"))
    present = [x for x in names if x in order]
    if present != [x for x in order if x in present]:
        problems.append(_p(n, "fields out of order"))
    lane = next((f[6:].strip() for f in fields if f.startswith("lane: ")), None)
    return problems, lane


def parse_tasks(text, kind="full", first_line=1):
    """kind: full (title+header+waves), section (waves), lines (task lines only)."""
    problems = []
    lines = text.split("\n")
    i = 0
    if kind == "full":
        if not lines[0].startswith("# Tasks: "):
            problems.append(_p(first_line, "missing '# Tasks: <title>' line"))
        if len(lines) < 2 or not re.match(r"base: \S", lines[1]):
            problems.append(_p(first_line + 1, "missing 'base:' header"))
        if len(lines) < 3 or not re.match(r"fix-cycles: \d+$", lines[2]):
            problems.append(_p(first_line + 2, "missing 'fix-cycles:' header"))
        i = 3
    heading_lanes = None
    current = None
    for idx in range(i, len(lines)):
        n = first_line + idx
        line = lines[idx]
        wm = WAVE_RE.match(line)
        if line.startswith("#") and re.match(r"^#{2,3} Wave", line) and not wm:
            problems.append(_p(n, "malformed wave heading"))
            heading_lanes = None
            current = None
            continue
        if wm:
            parts = wm.group(2).split(" · ")
            if parts[0].startswith("depends: "):
                if not re.match(r"depends: [TF]\d+(, [TF]\d+)*$", parts[0]):
                    problems.append(_p(n, "bad depends list"))
                parts = parts[1:]
            heading_lanes = set()
            for part in parts:
                lm = LANE_RE.match(part)
                if lm:
                    heading_lanes.add(lm.group(1))
            if not heading_lanes or len(heading_lanes) != len(parts):
                problems.append(_p(n, "wave heading must list 'lane X: <globs>'"))
            current = None
            continue
        tm = TASK_RE.match(line)
        if tm:
            if kind != "lines" and heading_lanes is None:
                problems.append(_p(n, "task before a wave heading"))
            tp, lane = _task_line(line, n)
            problems += tp
            if heading_lanes is not None and lane and lane not in heading_lanes:
                problems.append(_p(n, "lane %s not in wave heading" % lane))
            current = {"n": n, "done": tm.group(1) == "x", "evidence": False}
            current["ref"] = tm.group(2)
            _finish(problems, lines, idx, current)
            continue
    return problems


def _finish(problems, lines, idx, task):
    has_evidence = False
    j = idx + 1
    while j < len(lines) and EVIDENCE_RE.match(lines[j]):
        if lines[j].lstrip().startswith("evidence:"):
            has_evidence = True
        j += 1
    if task["done"] and not has_evidence:
        problems.append(_p(task["n"], "done task %s has no evidence line" % task["ref"]))
    if not task["done"] and has_evidence:
        problems.append(_p(task["n"], "open task %s must not have evidence" % task["ref"]))


def parse_explore(text, first_line=1):
    problems = []
    lines = text.split("\n")
    if not lines[0].startswith("# ") or len(lines[0]) < 3:
        problems.append(_p(first_line, "missing '# <title>' line"))
    mm = re.match(r"mode: (\S+)$", lines[1]) if len(lines) > 1 else None
    if not mm:
        problems.append(_p(first_line + 1, "missing 'mode:' line after the title"))
    elif mm.group(1) not in MODES:
        problems.append(_p(first_line + 1, "mode must be one of fast | medium | full"))
    heads = [(first_line + k, l[3:].strip()) for k, l in enumerate(lines) if l.startswith("## ")]
    names = [h for _, h in heads]
    tasks_at = None
    if "Tasks" in names:
        tasks_at = names.index("Tasks")
    core = names[:tasks_at] if tasks_at is not None else [h for h in names if not h.startswith("Wave ")]
    if core != list(SECTIONS):
        problems.append(_p(first_line, "sections must be Goal, Non-goals, Decisions, Risks in order, found %s" % core))
    if "Decisions" in names:
        start = names.index("Decisions")
        s = heads[start][0] - first_line + 1
        end = heads[start + 1][0] - first_line if start + 1 < len(heads) else len(lines)
        block = lines[s:end]
        decisions = [k for k, l in enumerate(block) if l.startswith("### ")]
        if not decisions:
            problems.append(_p(heads[start][0], "Decisions has no '### <title>' decision"))
        for d, k in enumerate(decisions):
            stop = decisions[d + 1] if d + 1 < len(decisions) else len(block)
            body = block[k + 1:stop]
            for label in ("Context", "Choice", "Rejected"):
                if not any(b.startswith("- **%s:**" % label) for b in body):
                    problems.append(_p(first_line + s + k, "decision %r missing %s" % (block[k][4:], label)))
    if tasks_at is not None:
        t_line = heads[tasks_at][0]
        body = "\n".join(lines[t_line - first_line + 1:])
        problems += parse_tasks(body, "section", t_line + 1)
    return problems


def markdown_blocks(text):
    """Yield (first_body_line, body) for each ```markdown fenced block."""
    lines = text.split("\n")
    k = 0
    while k < len(lines):
        if lines[k].strip() == "```markdown":
            j = k + 1
            while j < len(lines) and lines[j].strip() != "```":
                j += 1
            yield k + 2, "\n".join(lines[k + 1:j])
            k = j
        k += 1


def check_markdown(text):
    """Return (kind, problems) per grammar-bearing block; other blocks skipped."""
    results = []
    for first, body in markdown_blocks(text):
        lines = body.split("\n")
        content = [l for l in lines if l.strip()]
        if len(lines) > 1 and lines[1].startswith("mode:"):
            results.append(("explore", parse_explore(body, first)))
        elif lines[0].startswith("# Tasks:"):
            results.append(("tasks", parse_tasks(body, "full", first)))
        elif content and all(l.startswith("- [") for l in content):
            results.append(("lines", parse_tasks(body, "lines", first)))
    return results
