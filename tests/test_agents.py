import os
import unittest

import plugin

KEYS = ["name", "description", "tools", "model"]


class AgentsTest(unittest.TestCase):
    def test_flags_model_differing_from_d16(self):
        text = "---\nname: scanner\ndescription: d\ntools: Read\nmodel: opus\n---\nbody\n"
        problems = plugin.check_agent("scanner.md", text, {"scanner": "sonnet"})
        self.assertTrue(any("model" in p for p in problems), problems)

    def test_flags_name_differing_from_filename(self):
        text = "---\nname: other\ndescription: d\ntools: Read\nmodel: sonnet\n---\n"
        problems = plugin.check_agent("scanner.md", text, {"scanner": "sonnet"})
        self.assertTrue(any("name" in p for p in problems), problems)

    def test_flags_wrong_key_order(self):
        text = "---\nname: scanner\ntools: Read\ndescription: d\nmodel: sonnet\n---\n"
        problems = plugin.check_agent("scanner.md", text, {"scanner": "sonnet"})
        self.assertTrue(problems)

    def test_valid_agent_passes(self):
        text = "---\nname: scanner\ndescription: d\ntools: Read\nmodel: sonnet\n---\n"
        self.assertEqual(plugin.check_agent("scanner.md", text, {"scanner": "sonnet"}), [])

    def test_repo_agents(self):
        tiers = plugin.design_tiers(plugin.read("DESIGN.md"))
        files = sorted(os.listdir(os.path.join(plugin.PLUGIN, "agents")))
        self.assertEqual(len(files), 6, files)
        self.assertEqual(sorted(f[:-3] for f in files), sorted(tiers))
        for f in files:
            self.assertEqual(plugin.check_agent(f, plugin.read("plugin", "agents", f), tiers), [], f)


if __name__ == "__main__":
    unittest.main()
