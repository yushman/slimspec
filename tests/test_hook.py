import os
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, ".githooks", "pre-commit")


def run_hook(test_body):
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["git", "init", "-q", tmp], check=True)
        os.makedirs(os.path.join(tmp, "tests"))
        with open(os.path.join(tmp, "tests", "test_x.py"), "w") as f:
            f.write("import unittest\n\nclass T(unittest.TestCase):\n    def test_x(self):\n        %s\n" % test_body)
        return subprocess.run(["sh", HOOK], cwd=tmp, capture_output=True).returncode


class HookTest(unittest.TestCase):
    def test_exits_nonzero_when_a_test_fails(self):
        self.assertEqual(run_hook("self.fail('x')"), 1)

    def test_exits_zero_when_tests_pass(self):
        self.assertEqual(run_hook("pass"), 0)

    def test_is_executable(self):
        self.assertTrue(os.access(HOOK, os.X_OK))


if __name__ == "__main__":
    unittest.main()
