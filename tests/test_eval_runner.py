import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STUB = """#!/bin/sh
for last; do :; done
out="$STUB_OUT/$(basename "$PWD").txt"
{
  echo "prompt=$last"
  [ -d .git ] && echo git=yes
  [ -f calc/CLAUDE.md ] && echo fixture=yes
  [ -f seeded.txt ] && echo seed=yes
  git log --oneline | wc -l | tr -d ' ' | sed 's/^/commits=/'
} > "$out"
echo '{"type":"result","result":"done"}'
"""

CHECK = """import json, sys
print(json.dumps({"hard-ok": "%s"}))
"""


class RunnerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.evals = os.path.join(self.tmp, "evals")
        os.makedirs(self.evals)
        shutil.copy(os.path.join(ROOT, "evals", "run.sh"), self.evals)
        for f in ("verdict.py", "evallib.py"):
            p = os.path.join(ROOT, "evals", f)
            if os.path.exists(p):
                shutil.copy(p, self.evals)
        shutil.copytree(os.path.join(ROOT, "evals", "fixture"),
                        os.path.join(self.evals, "fixture"))
        self.stub = os.path.join(self.tmp, "stub.sh")
        self.out = os.path.join(self.tmp, "out")
        os.makedirs(self.out)
        with open(self.stub, "w") as f:
            f.write(STUB)
        os.chmod(self.stub, 0o755)

    def add_case(self, name, verdict="pass"):
        d = os.path.join(self.evals, "cases", name)
        os.makedirs(os.path.join(d, "seed"))
        with open(os.path.join(d, "prompt.md"), "w") as f:
            f.write("do the thing\n")
        with open(os.path.join(d, "seed", "seeded.txt"), "w") as f:
            f.write("seed\n")
        with open(os.path.join(d, "check.py"), "w") as f:
            f.write(CHECK % verdict)

    def run_sh(self, *args):
        env = dict(os.environ, SLIMSPEC_EVAL_CMD=self.stub, STUB_OUT=self.out)
        return subprocess.run(["sh", os.path.join(self.evals, "run.sh"), *args],
                              env=env, capture_output=True, text=True)

    def test_runs_host_in_git_sandbox_with_fixture_and_seed(self):
        self.add_case("dummy")
        r = self.run_sh("--runs", "1")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        files = os.listdir(self.out)
        self.assertEqual(len(files), 1)
        with open(os.path.join(self.out, files[0])) as f:
            got = f.read()
        for line in ("prompt=do the thing", "git=yes", "fixture=yes",
                     "seed=yes", "commits=1"):
            self.assertIn(line, got)

    def test_saves_logs_and_check_output_per_run(self):
        self.add_case("dummy")
        self.run_sh("--runs", "2")
        res = os.path.join(self.evals, "results")
        stamp = os.path.join(res, os.listdir(res)[0])
        for run in ("1", "2"):
            d = os.path.join(stamp, "dummy", run)
            for f in ("stdout.log", "stderr.log", "check.json"):
                self.assertTrue(os.path.isfile(os.path.join(d, f)), d + f)

    def test_case_filter_and_default_runs(self):
        self.add_case("a")
        self.add_case("b")
        self.run_sh("--case", "a")
        self.assertEqual(len(os.listdir(self.out)), 3)

    def test_exit_code_follows_verdict(self):
        self.add_case("good")
        self.assertEqual(self.run_sh("--runs", "2").returncode, 0)
        self.add_case("bad", verdict="fail")
        r = self.run_sh("--runs", "2")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("FAIL bad", r.stdout)
        self.assertIn("PASS good", r.stdout)

    def test_sandbox_git_ignores_outer_git_env(self):
        self.add_case("dummy")
        outer = os.path.join(self.tmp, "outer")
        os.makedirs(outer)
        g = dict(os.environ)
        for k in ("GIT_DIR", "GIT_INDEX_FILE", "GIT_WORK_TREE"):
            g.pop(k, None)
        subprocess.run(["git", "init", "-q"], cwd=outer, env=g, check=True)
        index = os.path.join(outer, ".git", "index")
        with open(os.path.join(outer, "f.txt"), "w") as f:
            f.write("x\n")
        subprocess.run(["git", "add", "f.txt"], cwd=outer, env=g, check=True)
        with open(index, "rb") as f:
            before = f.read()
        env = dict(os.environ, SLIMSPEC_EVAL_CMD=self.stub, STUB_OUT=self.out,
                   GIT_DIR=os.path.join(outer, ".git"), GIT_WORK_TREE=outer,
                   GIT_INDEX_FILE=index)
        r = subprocess.run(["sh", os.path.join(self.evals, "run.sh"), "--runs", "1"],
                           env=env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        with open(index, "rb") as f:
            self.assertEqual(f.read(), before)

    def test_unknown_case_exits_nonzero(self):
        self.add_case("dummy")
        r = self.run_sh("--case", "nope")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("no cases ran", r.stdout + r.stderr)

    def test_zero_runs_exits_nonzero(self):
        self.add_case("dummy")
        self.assertNotEqual(self.run_sh("--runs", "0").returncode, 0)

    def test_option_without_value_exits_2(self):
        self.add_case("dummy")
        for opt in ("--runs", "--case"):
            try:
                r = subprocess.run(
                    ["sh", os.path.join(self.evals, "run.sh"), opt],
                    env=dict(os.environ, SLIMSPEC_EVAL_CMD=self.stub,
                             STUB_OUT=self.out),
                    capture_output=True, text=True, timeout=10)
            except subprocess.TimeoutExpired:
                self.fail(opt + " without a value hangs")
            self.assertEqual(r.returncode, 2, opt)
            self.assertIn("usage", r.stderr)

    def test_gitignore_has_results(self):
        with open(os.path.join(ROOT, ".gitignore")) as f:
            self.assertIn("evals/results/", f.read().split("\n"))

    def test_fixture_tests_pass(self):
        r = subprocess.run(["python3", "-m", "unittest"],
                           cwd=os.path.join(ROOT, "evals", "fixture"),
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main()
