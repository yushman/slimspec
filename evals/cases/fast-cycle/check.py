import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

import evallib  # noqa: E402


def read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def folder_gone(sandbox):
    base = os.path.join(sandbox, ".slimspec", "changes")
    return not os.path.isdir(base) or not os.listdir(base)


def tests_cover_mul(sandbox):
    tdir = os.path.join(sandbox, "tests")
    for name in sorted(os.listdir(tdir)) if os.path.isdir(tdir) else []:
        if name.endswith(".py") and re.search(r"\bmul\b", read(os.path.join(tdir, name))):
            return True
    return False


def final_explore(trace):
    uses = evallib._tool_uses(trace)
    if uses == evallib.SKIPPED:
        return evallib.SKIPPED
    text = None
    for name, inp in uses:
        if not str(inp.get("file_path") or "").endswith("explore.md"):
            continue
        if name == "Write":
            text = inp.get("content") or ""
        elif name == "Edit" and text is not None:
            old, new = inp.get("old_string") or "", inp.get("new_string") or ""
            text = text.replace(old, new) if inp.get("replace_all") else text.replace(old, new, 1)
    return text


def explore_tasks(trace):
    last = final_explore(trace)
    if last == evallib.SKIPPED:
        return evallib.SKIPPED
    if not last or "## Tasks" not in last or evallib.grammar().parse_explore(last):
        return "fail"
    return "pass" if re.search(r"evidence: red .* green ", last) else "fail"


def checks(sandbox, trace):
    code = read(os.path.join(sandbox, "calc", "calc.py"))
    spec = read(os.path.join(sandbox, "calc", "CLAUDE.md"))
    ok = lambda b: "pass" if b else "fail"
    return {
        "hard-tests-green": ok(evallib.fixture_tests_pass(sandbox)),
        "hard-code-and-test": ok(re.search(r"def mul\(", code) and tests_cover_mul(sandbox)),
        "hard-spec-updated": ok(re.search(r"\bmul\b", spec)),
        "hard-change-folder-gone": ok(folder_gone(sandbox)),
        "explore-tasks-grammar": explore_tasks(trace),
        "implementer-launched": evallib.launched(trace, "slimspec:implementer"),
    }


if __name__ == "__main__":
    evallib.report(checks(sys.argv[1], read(sys.argv[2])))
