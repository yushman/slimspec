import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

import evallib  # noqa: E402


def with_tax(sandbox, amount):
    r = subprocess.run(
        [sys.executable, "-c", "from calc.calc import with_tax; print(with_tax(%d))" % amount],
        cwd=sandbox, capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return None


def checks(sandbox, trace):
    reflects = with_tax(sandbox, 100) == 120 and with_tax(sandbox, 50) == 60
    return {
        "hard-tests-green": "pass" if evallib.fixture_tests_pass(sandbox) else "fail",
        "hard-answer-reflected": "pass" if reflects else "fail",
        "implementer-launched-twice": evallib.launched(trace, "slimspec:implementer", 2),
    }


if __name__ == "__main__":
    try:
        with open(sys.argv[2], encoding="utf-8") as f:
            trace = f.read()
    except OSError:
        trace = ""
    evallib.report(checks(sys.argv[1], trace))
