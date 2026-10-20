import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "evals"))

import evallib  # noqa: E402


def tool(name, **inp):
    return {"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": name, "input": inp}]}}


def stream(*events):
    return "\n".join(json.dumps(e) for e in events) + "\n"


TRACE = stream(
    {"type": "system", "subtype": "init"},
    tool("Agent", subagent_type="slimspec:implementer", prompt="x"),
    tool("Write", file_path="/s/a.md", content="one"),
    tool("Edit", file_path="/s/b.py", old_string="x", new_string="two"),
    tool("Write", file_path="/s/a.md", content="three"),
    tool("Agent", subagent_type="slimspec:implementer", prompt="y"),
    {"type": "result", "result": "all done"},
)
RAW = "plain text\nfinal line\n"


class TraceTest(unittest.TestCase):
    def test_detects_stream_json(self):
        self.assertTrue(evallib.is_stream_json(TRACE))
        self.assertFalse(evallib.is_stream_json(RAW))
        self.assertFalse(evallib.is_stream_json(""))

    def test_trace_checks_skipped_when_not_stream_json(self):
        self.assertEqual(evallib.agent_launches(RAW), evallib.SKIPPED)
        self.assertEqual(evallib.tool_writes(RAW), evallib.SKIPPED)
        self.assertEqual(evallib.launched(RAW, "slimspec:implementer"),
                         "skipped")

    def test_agent_launches_by_subagent_type(self):
        self.assertEqual(evallib.agent_launches(TRACE),
                         ["slimspec:implementer", "slimspec:implementer"])
        self.assertEqual(evallib.launched(TRACE, "slimspec:implementer", 2),
                         "pass")
        self.assertEqual(evallib.launched(TRACE, "slimspec:planner"), "fail")
        self.assertEqual(evallib.launched(TRACE, "slimspec:implementer", 3),
                         "fail")

    def test_tool_writes_per_path(self):
        w = evallib.tool_writes(TRACE)
        self.assertEqual(w["/s/a.md"], ["one", "three"])
        self.assertEqual(w["/s/b.py"], ["two"])

    def test_last_message(self):
        self.assertEqual(evallib.last_message(TRACE), "all done")
        self.assertEqual(evallib.last_message(RAW), RAW)


class SandboxTest(unittest.TestCase):
    def setUp(self):
        self.sb = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.sb, True)
        shutil.copytree(os.path.join(ROOT, "evals", "fixture"), self.sb,
                        dirs_exist_ok=True)
        git = ["git", "-c", "user.name=t", "-c", "user.email=t@t"]
        subprocess.run(["git", "init", "-q"], cwd=self.sb, check=True)
        subprocess.run(["git", "add", "-A"], cwd=self.sb, check=True)
        subprocess.run(git + ["commit", "-qm", "i"], cwd=self.sb, check=True)

    def test_changed_paths(self):
        with open(os.path.join(self.sb, "calc", "calc.py"), "a") as f:
            f.write("\n")
        os.makedirs(os.path.join(self.sb, "new"))
        with open(os.path.join(self.sb, "new", "x.txt"), "w") as f:
            f.write("x")
        os.remove(os.path.join(self.sb, "calc", "CLAUDE.md"))
        self.assertEqual(evallib.changed_paths(self.sb),
                         ["calc/CLAUDE.md", "calc/calc.py", "new/x.txt"])

    def test_fixture_tests_result(self):
        self.assertTrue(evallib.fixture_tests_pass(self.sb))
        with open(os.path.join(self.sb, "calc", "calc.py"), "w") as f:
            f.write("def add(a, b):\n    return 0\n")
        self.assertFalse(evallib.fixture_tests_pass(self.sb))


class MiscTest(unittest.TestCase):
    def test_report_prints_json(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            evallib.report({"hard-a": "pass", "b": "skipped"})
        self.assertEqual(json.loads(buf.getvalue()),
                         {"hard-a": "pass", "b": "skipped"})

    def test_grammar_import(self):
        grammar_path = os.path.join(ROOT, "tests", "grammar.py")
        if not os.path.exists(grammar_path):
            self.skipTest("tests/grammar.py not written yet (lane A)")
        self.assertTrue(hasattr(evallib.grammar(), "parse_tasks"))


if __name__ == "__main__":
    unittest.main()
