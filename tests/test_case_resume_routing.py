import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASE = os.path.join(ROOT, "evals", "cases", "resume-routing")
sys.path.insert(0, ROOT + "/tests")
import grammar  # noqa: E402


def load_check():
    spec = importlib.util.spec_from_file_location("rr_check", os.path.join(CASE, "check.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def make_sandbox(tmp):
    box = os.path.join(tmp, "box")
    shutil.copytree(os.path.join(ROOT, "evals", "fixture"), box)
    shutil.copytree(os.path.join(CASE, "seed"), box, dirs_exist_ok=True)
    for cmd in (["init", "-q"], ["add", "-A"],
                ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "i"]):
        subprocess.run(["git"] + cmd, cwd=box, check=True)
    return box


TASKS = """# Tasks: Add mul to calc
base: none
fix-cycles: 0

## Wave 1 (lane A: calc/*, tests/*)
One lane.
- [ ] T1 · lane: A · files: calc/calc.py, tests/test_calc.py · test-first: "mul multiplies" · done: mul(2, 3) is 6
"""


def stream(*agents):
    return "\n".join(json.dumps({"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": "Agent", "input": {"subagent_type": a}}]}}) for a in agents) + "\n"


class ResumeRoutingCheckTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)
        self.box = make_sandbox(self.tmp)
        self.log = os.path.join(self.tmp, "out.log")
        self.write_log("plain text\n")
        self.check = load_check()

    def write_log(self, text):
        with open(self.log, "w") as f:
            f.write(text)

    def write_tasks(self, text):
        with open(os.path.join(self.box, ".slimspec", "changes", "add-mul", "tasks.md"), "w") as f:
            f.write(text)

    def run_check(self):
        return self.check.checks(self.box, self.log)

    def test_seed_explore_passes_grammar(self):
        path = os.path.join(CASE, "seed", ".slimspec", "changes", "add-mul", "explore.md")
        with open(path) as f:
            self.assertEqual(grammar.parse_explore(f.read()), [])
        self.assertFalse(os.path.exists(path.replace("explore.md", "tasks.md")))

    def test_correct_outcome_passes(self):
        self.write_tasks(TASKS)
        self.write_log(stream("slimspec:planner"))
        r = self.run_check()
        self.assertEqual(r, {"hard-tasks-md-valid": "pass", "hard-no-source-changed": "pass",
                             "planner-launched": "pass", "no-implementer-launched": "pass"})

    def test_fails_when_source_files_changed(self):
        self.write_tasks(TASKS)
        with open(os.path.join(self.box, "calc", "calc.py"), "a") as f:
            f.write("\ndef mul(a, b):\n    return a * b\n")
        self.assertEqual(self.run_check()["hard-no-source-changed"], "fail")

    def test_fails_when_test_file_added(self):
        self.write_tasks(TASKS)
        with open(os.path.join(self.box, "tests", "test_mul.py"), "w") as f:
            f.write("")
        self.assertEqual(self.run_check()["hard-no-source-changed"], "fail")

    def test_fails_without_tasks_md(self):
        self.assertEqual(self.run_check()["hard-tasks-md-valid"], "fail")

    def test_fails_on_grammar_problem(self):
        self.write_tasks(TASKS.replace(" · done: mul(2, 3) is 6", ""))
        self.assertEqual(self.run_check()["hard-tasks-md-valid"], "fail")

    def test_implementer_launch_fails_soft_check(self):
        self.write_tasks(TASKS)
        self.write_log(stream("slimspec:planner", "slimspec:implementer"))
        self.assertEqual(self.run_check()["no-implementer-launched"], "fail")

    def test_trace_checks_skipped_without_stream_json(self):
        self.write_tasks(TASKS)
        r = self.run_check()
        self.assertEqual(r["planner-launched"], "skipped")
        self.assertEqual(r["no-implementer-launched"], "skipped")


if __name__ == "__main__":
    unittest.main()
