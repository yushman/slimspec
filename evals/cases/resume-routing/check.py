import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

import evallib  # noqa: E402

SLUG = "add-mul"


def checks(sandbox, log):
    tasks = os.path.join(sandbox, ".slimspec", "changes", SLUG, "tasks.md")
    exists = os.path.isfile(tasks)
    problems = []
    if exists:
        with open(tasks, encoding="utf-8") as f:
            problems = evallib.grammar().parse_tasks(f.read())
    changed = [p for p in evallib.changed_paths(sandbox)
               if (p.startswith("calc/") or p.startswith("tests/")) and "__pycache__" not in p]
    with open(log, encoding="utf-8") as f:
        text = f.read()
    return {
        "hard-tasks-md-valid": "pass" if exists and not problems else "fail",
        "hard-no-source-changed": "pass" if not changed else "fail",
        "planner-launched": evallib.launched(text, "slimspec:planner"),
        "no-implementer-launched": _negate(evallib.launched(text, "slimspec:implementer")),
    }


def _negate(result):
    return {"pass": "fail", "fail": "pass"}.get(result, result)


if __name__ == "__main__":
    evallib.report(checks(sys.argv[1], sys.argv[2]))
