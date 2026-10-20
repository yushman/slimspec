import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

import evallib  # noqa: E402

SLUG = "add-mul"
SPEC = "calc/CLAUDE.md"
FOLDER = ".slimspec/changes/%s/" % SLUG


def checks(sandbox, log):
    changed = [p for p in evallib.changed_paths(sandbox) if "__pycache__" not in p]
    outside = [p for p in changed if not p.startswith(FOLDER)]
    config = os.path.isfile(os.path.join(sandbox, ".slimspec", "config.yaml"))
    with open(log, encoding="utf-8") as f:
        text = f.read()
    return {
        "hard-only-spec-changed": "pass" if all(p == SPEC for p in outside) else "fail",
        "hard-change-folder-deleted": "pass" if not os.path.exists(os.path.join(sandbox, FOLDER)) else "fail",
        "hard-config-intact": "pass" if config and ".slimspec/config.yaml" not in changed else "fail",
        "grounder-launched": evallib.launched(text, "slimspec:grounder"),
    }


if __name__ == "__main__":
    evallib.report(checks(sys.argv[1], sys.argv[2]))
