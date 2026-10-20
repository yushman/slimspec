import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASE = os.path.join(ROOT, "evals", "cases", "blocked-relaunch")
sys.path.insert(0, os.path.join(ROOT, "evals"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

import grammar  # noqa: E402

_spec = importlib.util.spec_from_file_location("check_blocked_relaunch", os.path.join(CASE, "check.py"))
check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check)

CHANGE = os.path.join(CASE, "seed", ".slimspec", "changes", "with-tax")


def sandbox(rate=20, with_fn=True, test=True):
    d = tempfile.mkdtemp()
    shutil.copytree(os.path.join(ROOT, "evals", "fixture"), d, dirs_exist_ok=True)
    shutil.copytree(os.path.join(CASE, "seed"), d, dirs_exist_ok=True)
    with open(os.path.join(d, "calc", "rates.py"), "w") as f:
        f.write("RATE = %s\n" % rate)
    if with_fn:
        with open(os.path.join(d, "calc", "calc.py"), "a") as f:
            f.write("\n\ndef with_tax(amount):\n"
                    "    from calc.rates import RATE\n"
                    "    return amount * (100 + RATE) / 100\n")
    if test:
        with open(os.path.join(d, "tests", "test_calc.py"), "a") as f:
            f.write("\n\nclass TaxTest(unittest.TestCase):\n"
                    "    def test_tax(self):\n"
                    "        from calc.calc import with_tax\n"
                    "        self.assertEqual(with_tax(100), 120)\n")
    subprocess.run(["git", "init", "-q"], cwd=d, check=True)
    return d


def trace(n):
    ev = [{"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": "Agent",
         "input": {"subagent_type": "slimspec:implementer"}}]}} for _ in range(n)]
    return "\n".join(json.dumps(e) for e in ev) + "\n"


class BlockedRelaunchCheckTest(unittest.TestCase):
    def run_check(self, t="", **kw):
        d = sandbox(**kw)
        self.addCleanup(shutil.rmtree, d)
        return check.checks(d, t)

    def test_seed_is_valid_and_open(self):
        with open(os.path.join(CHANGE, "explore.md")) as f:
            self.assertEqual(grammar.parse_explore(f.read()), [])
        with open(os.path.join(CHANGE, "tasks.md")) as f:
            text = f.read()
        self.assertEqual(grammar.parse_tasks(text), [])
        self.assertIn("- [ ] T1", text)
        self.assertNotIn("rates.py", text.split("files:")[1].split("·")[0])

    def test_seed_fixture_tests_pass(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d)
        shutil.copytree(os.path.join(ROOT, "evals", "fixture"), d, dirs_exist_ok=True)
        shutil.copytree(os.path.join(CASE, "seed"), d, dirs_exist_ok=True)
        subprocess.run(["git", "init", "-q"], cwd=d, check=True)
        import evallib
        self.assertTrue(evallib.fixture_tests_pass(d))

    def test_correct_outcome_passes(self):
        r = self.run_check(trace(2))
        self.assertEqual(set(r.values()), {"pass"}, r)

    def test_fails_when_code_ignores_the_stated_answer(self):
        r = self.run_check(rate=0)
        self.assertEqual(r["hard-answer-reflected"], "fail")
        r = self.run_check(rate=15)
        self.assertEqual(r["hard-answer-reflected"], "fail")

    def test_fails_when_function_missing(self):
        r = self.run_check(with_fn=False, test=False)
        self.assertEqual(r["hard-answer-reflected"], "fail")

    def test_fails_when_tests_red(self):
        r = self.run_check(rate=15)
        self.assertEqual(r["hard-tests-green"], "fail")

    def test_soft_launch_count(self):
        self.assertEqual(self.run_check(trace(1))["implementer-launched-twice"], "fail")
        self.assertEqual(self.run_check("raw\n")["implementer-launched-twice"], "skipped")

    def test_cli_prints_json(self):
        d = sandbox()
        self.addCleanup(shutil.rmtree, d)
        log = os.path.join(d, "..", "br.log")
        with open(log, "w") as f:
            f.write("raw\n")
        self.addCleanup(os.remove, log)
        out = subprocess.run([sys.executable, os.path.join(CASE, "check.py"), d, log],
                             capture_output=True, text=True, check=True).stdout
        self.assertEqual(json.loads(out)["hard-answer-reflected"], "pass")

    def test_prompt_runs_apply_with_answer(self):
        with open(os.path.join(CASE, "prompt.md")) as f:
            t = f.read()
        self.assertIn("/slimspec:apply with-tax", t)
        self.assertIn("RATE = 20", t)


if __name__ == "__main__":
    unittest.main()
