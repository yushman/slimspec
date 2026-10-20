import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASE = os.path.join(ROOT, "evals", "cases", "ground-scope")
sys.path.insert(0, ROOT + "/tests")
import grammar  # noqa: E402

FOLDER = os.path.join(".slimspec", "changes", "add-mul")


def load_check():
    spec = importlib.util.spec_from_file_location("gs_check", os.path.join(CASE, "check.py"))
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


class GroundScopeCheckTest(unittest.TestCase):
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

    def good_outcome(self):
        shutil.rmtree(os.path.join(self.box, FOLDER))
        with open(os.path.join(self.box, "calc", "CLAUDE.md"), "a") as f:
            f.write("- `calc.calc.mul(a, b)` returns the product.\n")

    def run_check(self):
        return self.check.checks(self.box, self.log)

    def test_seed_change_passes_grammar(self):
        d = os.path.join(CASE, "seed", FOLDER)
        with open(os.path.join(d, "explore.md")) as f:
            self.assertEqual(grammar.parse_explore(f.read()), [])
        with open(os.path.join(d, "tasks.md")) as f:
            text = f.read()
        self.assertEqual(grammar.parse_tasks(text), [])
        self.assertNotIn("- [ ]", text)
        self.assertTrue(os.path.isfile(os.path.join(CASE, "seed", ".slimspec", "config.yaml")))

    def test_correct_outcome_passes(self):
        self.good_outcome()
        self.write_log(json.dumps({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Agent", "input": {"subagent_type": "slimspec:grounder"}}]}}) + "\n")
        self.assertEqual(self.run_check(), {
            "hard-only-spec-changed": "pass", "hard-change-folder-deleted": "pass",
            "hard-config-intact": "pass", "grounder-launched": "pass"})

    def test_untouched_spec_still_passes_hard_checks(self):
        shutil.rmtree(os.path.join(self.box, FOLDER))
        r = self.run_check()
        self.assertEqual([k for k, v in r.items() if k.startswith("hard") and v != "pass"], [])

    def test_fails_when_config_deleted(self):
        self.good_outcome()
        os.remove(os.path.join(self.box, ".slimspec", "config.yaml"))
        r = self.run_check()
        self.assertEqual(r["hard-config-intact"], "fail")

    def test_fails_when_change_folder_remains(self):
        with open(os.path.join(self.box, "calc", "CLAUDE.md"), "a") as f:
            f.write("x\n")
        self.assertEqual(self.run_check()["hard-change-folder-deleted"], "fail")

    def test_fails_when_code_changed(self):
        self.good_outcome()
        with open(os.path.join(self.box, "calc", "calc.py"), "a") as f:
            f.write("\n")
        self.assertEqual(self.run_check()["hard-only-spec-changed"], "fail")

    def test_fails_when_other_slimspec_content_removed(self):
        self.good_outcome()
        shutil.rmtree(os.path.join(self.box, ".slimspec"))
        r = self.run_check()
        self.assertEqual(r["hard-only-spec-changed"], "fail")

    def test_trace_check_skipped_without_stream_json(self):
        self.good_outcome()
        self.assertEqual(self.run_check()["grounder-launched"], "skipped")


if __name__ == "__main__":
    unittest.main()
