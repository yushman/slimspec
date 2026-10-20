import os
import tempfile
import unittest

import plugin


class RefsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        os.makedirs(os.path.join(self.root, "skills", "a"))
        with open(os.path.join(self.root, "skills", "a", "x.md"), "w") as f:
            f.write("x")
        self.file = os.path.join(self.root, "skills", "a", "SKILL.md")

    def tearDown(self):
        self.tmp.cleanup()

    def test_flags_unresolvable_plugin_root_path(self):
        text = "ok\nRead `${CLAUDE_PLUGIN_ROOT}/skills/a/nope.md` now.\n"
        problems = plugin.check_paths(self.file, text, self.root)
        self.assertEqual(len(problems), 1, problems)
        self.assertIn(":2:", problems[0])

    def test_accepts_resolvable_plugin_root_path(self):
        text = "Read `${CLAUDE_PLUGIN_ROOT}/skills/a/x.md`."
        self.assertEqual(plugin.check_paths(self.file, text, self.root), [])

    def test_skips_placeholders(self):
        text = "`${CLAUDE_PLUGIN_ROOT}/skills/<phase>/SKILL.md`"
        self.assertEqual(plugin.check_paths(self.file, text, self.root), [])

    def test_flags_broken_relative_link(self):
        problems = plugin.check_paths(self.file, "see [n](nope.md#top)", self.root)
        self.assertEqual(len(problems), 1, problems)

    def test_accepts_link_with_anchor_and_ignores_urls(self):
        text = "[x](x.md#sec) [u](https://e.com/a.md) [h](#here)"
        self.assertEqual(plugin.check_paths(self.file, text, self.root), [])

    def test_repo_paths_resolve(self):
        problems = []
        for f in plugin.md_files("skills", "agents"):
            with open(f, encoding="utf-8") as fh:
                problems += plugin.check_paths(f, fh.read(), plugin.ROOT)
        self.assertEqual(problems, [])


class AgentRefsTest(unittest.TestCase):
    AGENTS = {"scanner", "planner"}
    SKILLS = {"apply"}

    def check(self, text):
        return plugin.check_agent_refs("skills/x/SKILL.md", text, self.AGENTS, self.SKILLS)

    def test_flags_unknown_agent(self):
        problems = self.check("a\nLaunch `slimspec:ghost` now")
        self.assertEqual(len(problems), 1, problems)
        self.assertIn(":2:", problems[0])

    def test_flags_unknown_in_pipe_list(self):
        self.assertEqual(len(self.check("`slimspec:scanner | planner | ghost`")), 1)

    def test_accepts_known_and_commands(self):
        text = "`slimspec:scanner | planner` and /slimspec:apply and slimspec:apply and slimspec: prose"
        self.assertEqual(self.check(text), [])

    def test_repo_agent_refs(self):
        base = os.path.join(plugin.ROOT, "skills")
        skills = {d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))}
        agents = {f[:-3] for f in os.listdir(os.path.join(plugin.ROOT, "agents"))}
        problems = []
        for f in plugin.md_files("skills"):
            with open(f, encoding="utf-8") as fh:
                problems += plugin.check_agent_refs(f, fh.read(), agents, skills)
        self.assertEqual(problems, [])


if __name__ == "__main__":
    unittest.main()
