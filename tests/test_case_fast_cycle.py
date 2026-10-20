import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASE = os.path.join(ROOT, "evals", "cases", "fast-cycle")
sys.path.insert(0, os.path.join(ROOT, "evals"))


_spec = importlib.util.spec_from_file_location("check_fast_cycle", os.path.join(CASE, "check.py"))
check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check)


EXPLORE = """# Explore: mul
mode: fast

## Goal
Add mul.

## Non-goals
Nothing else.

## Decisions
### Plain multiply
- **Context:** need a product.
- **Choice:** a * b.
- **Rejected:** reduce.

## Risks
None.

## Tasks

## Wave 1 (lane A: calc/*, tests/*)
One lane.
- [x] T1 · lane: A · files: calc/calc.py, tests/test_calc.py · test-first: "mul multiplies" · done: mul(2, 3) is 6
  evidence: red "mul multiplies — FAIL" · green "2 passed"
"""


def sandbox(code=True, test=True, spec=True, folder=False):
    d = tempfile.mkdtemp()
    shutil.copytree(os.path.join(ROOT, "evals", "fixture"), d, dirs_exist_ok=True)
    with open(os.path.join(d, "calc", "calc.py"), "a") as f:
        if code:
            f.write("\n\ndef mul(a, b):\n    return a * b\n")
    with open(os.path.join(d, "tests", "test_calc.py"), "a") as f:
        if test:
            f.write("\n\nclass MulTest(unittest.TestCase):\n"
                    "    def test_mul(self):\n"
                    "        from calc.calc import mul\n"
                    "        self.assertEqual(mul(2, 3), 6)\n")
    if spec:
        with open(os.path.join(d, "calc", "CLAUDE.md"), "a") as f:
            f.write("- `calc.calc.mul(a, b)` returns the product.\n")
    if folder:
        os.makedirs(os.path.join(d, ".slimspec", "changes", "mul"))
    subprocess.run(["git", "init", "-q"], cwd=d, check=True)
    return d


def trace(explore, agent="slimspec:implementer"):
    def tu(name, **inp):
        return {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": name, "input": inp}]}}
    ev = [tu("Agent", subagent_type=agent, prompt="x"),
          tu("Write", file_path="/s/.slimspec/changes/mul/explore.md", content=explore)]
    return "\n".join(json.dumps(e) for e in ev) + "\n"


def write_then_edit_trace():
    def tu(name, **inp):
        return {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": name, "input": inp}]}}
    path = "/s/.slimspec/changes/mul/explore.md"
    unticked = EXPLORE.replace("- [x] T1", "- [ ] T1").replace(
        '  evidence: red "mul multiplies — FAIL" · green "2 passed"\n', "")
    ev = [tu("Agent", subagent_type="slimspec:implementer", prompt="x"),
          tu("Write", file_path=path, content=unticked),
          tu("Edit", file_path=path, old_string="- [ ] T1", new_string="- [x] T1"),
          tu("Edit", file_path=path, old_string='done: mul(2, 3) is 6\n',
             new_string='done: mul(2, 3) is 6\n  evidence: red "mul multiplies — FAIL" · green "2 passed"\n')]
    return "\n".join(json.dumps(e) for e in ev) + "\n"


class FastCycleCheckTest(unittest.TestCase):
    def run_check(self, **kw):
        d = sandbox(**kw)
        self.addCleanup(shutil.rmtree, d)
        return check.checks(d, kw_trace.get("t", ""))

    def test_correct_outcome_passes_everything(self):
        kw_trace["t"] = trace(EXPLORE)
        r = self.run_check()
        self.assertEqual(set(r.values()), {"pass"}, r)

    def test_fails_when_change_folder_still_exists(self):
        kw_trace["t"] = trace(EXPLORE)
        self.assertEqual(self.run_check(folder=True)["hard-change-folder-gone"], "fail")

    def test_fails_without_code_test_or_spec(self):
        kw_trace["t"] = trace(EXPLORE)
        self.assertEqual(self.run_check(code=False, test=False)["hard-code-and-test"], "fail")
        self.assertEqual(self.run_check(test=False)["hard-code-and-test"], "fail")
        self.assertEqual(self.run_check(spec=False)["hard-spec-updated"], "fail")

    def test_fails_when_tests_red(self):
        kw_trace["t"] = ""
        self.assertEqual(self.run_check(code=False)["hard-tests-green"], "fail")

    def test_soft_checks_skipped_without_trace(self):
        kw_trace["t"] = "plain output\n"
        r = self.run_check()
        self.assertEqual(r["explore-tasks-grammar"], "skipped")
        self.assertEqual(r["implementer-launched"], "skipped")

    def test_soft_checks_fail_on_bad_trace(self):
        kw_trace["t"] = trace(EXPLORE.replace("mode: fast", ""), agent="slimspec:planner")
        r = self.run_check()
        self.assertEqual(r["explore-tasks-grammar"], "fail")
        self.assertEqual(r["implementer-launched"], "fail")
        kw_trace["t"] = trace(EXPLORE.split("## Tasks")[0])
        self.assertEqual(self.run_check()["explore-tasks-grammar"], "fail")

    def test_write_then_edits_are_replayed(self):
        kw_trace["t"] = write_then_edit_trace()
        self.assertEqual(self.run_check()["explore-tasks-grammar"], "pass")

    def test_cli_prints_json(self):
        d = sandbox()
        self.addCleanup(shutil.rmtree, d)
        log = os.path.join(d, "..", "fc.log")
        with open(log, "w") as f:
            f.write("raw\n")
        self.addCleanup(os.remove, log)
        out = subprocess.run([sys.executable, os.path.join(CASE, "check.py"), d, log],
                             capture_output=True, text=True, check=True).stdout
        self.assertEqual(json.loads(out)["hard-tests-green"], "pass")

    def test_prompt_exists(self):
        with open(os.path.join(CASE, "prompt.md")) as f:
            self.assertIn("/slimspec:fast", f.read())


kw_trace = {}

if __name__ == "__main__":
    unittest.main()
