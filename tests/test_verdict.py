import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "evals"))

import verdict  # noqa: E402


class JudgeTest(unittest.TestCase):
    def test_hard_check_failing_in_one_of_three_runs_fails(self):
        runs = [{"hard-x": "pass"}, {"hard-x": "fail"}, {"hard-x": "pass"}]
        self.assertEqual(verdict.judge(runs)["hard-x"], "fail")

    def test_soft_check_passes_on_majority(self):
        runs = [{"soft": "pass"}, {"soft": "fail"}, {"soft": "pass"}]
        self.assertEqual(verdict.judge(runs)["soft"], "pass")

    def test_soft_check_fails_without_majority(self):
        runs = [{"soft": "pass"}, {"soft": "fail"}, {"soft": "fail"}]
        self.assertEqual(verdict.judge(runs)["soft"], "fail")

    def test_skipped_runs_do_not_count(self):
        runs = [{"soft": "skipped"}, {"soft": "pass"}, {"soft": "skipped"}]
        self.assertEqual(verdict.judge(runs)["soft"], "pass")

    def test_all_skipped_is_skipped(self):
        runs = [{"t": "skipped"}, {"t": "skipped"}]
        self.assertEqual(verdict.judge(runs)["t"], "skipped")

    def test_hard_skipped_in_some_runs_still_needs_the_rest(self):
        runs = [{"hard-x": "skipped"}, {"hard-x": "pass"}]
        self.assertEqual(verdict.judge(runs)["hard-x"], "pass")


class CliTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def write(self, case, run, data):
        d = os.path.join(self.tmp, case, str(run))
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "check.json"), "w") as f:
            f.write(data if isinstance(data, str) else json.dumps(data))

    def cli(self):
        return subprocess.run(
            [sys.executable, os.path.join(ROOT, "evals", "verdict.py"), self.tmp],
            capture_output=True, text=True)

    def test_prints_per_case_and_check_and_exits_1_on_failure(self):
        for i, v in enumerate(["pass", "fail", "pass"], 1):
            self.write("c1", i, {"hard-a": v, "soft-b": "pass"})
        r = self.cli()
        self.assertEqual(r.returncode, 1)
        self.assertIn("FAIL c1", r.stdout)
        self.assertIn("fail hard-a", r.stdout)
        self.assertIn("pass soft-b", r.stdout)

    def test_exits_0_when_all_cases_pass(self):
        for i in (1, 2):
            self.write("c1", i, {"hard-a": "pass", "t": "skipped"})
        r = self.cli()
        self.assertEqual(r.returncode, 0)
        self.assertIn("PASS c1", r.stdout)
        self.assertIn("skipped t", r.stdout)

    def test_unparseable_check_output_fails_the_case(self):
        self.write("c1", 1, "not json")
        self.assertEqual(self.cli().returncode, 1)


if __name__ == "__main__":
    unittest.main()
