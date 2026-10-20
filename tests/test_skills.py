import os
import unittest

import plugin


class SkillsTest(unittest.TestCase):
    def test_flags_skill_dir_missing_from_layout(self):
        self.assertTrue(plugin.check_skill_dirs(["a", "b"], {"a"}))

    def test_flags_layout_dir_without_skill(self):
        self.assertTrue(plugin.check_skill_dirs(["a"], {"a", "b"}))

    def test_equal_sets_pass(self):
        self.assertEqual(plugin.check_skill_dirs(["a"], {"a"}), [])

    def test_flags_name_mismatch(self):
        self.assertTrue(plugin.check_skill("x", "---\nname: y\ndescription: d\n---\n"))

    def test_flags_missing_description(self):
        self.assertTrue(plugin.check_skill("x", "---\nname: x\n---\n"))

    def test_layout_parse_ignores_top_level(self):
        design = "## Layout\n\n```\nslimspec/\n  plugin/\n    skills/\n      a/  # c\n      b/\n    agents/\n      x.md\n  tests/\n```\n"
        self.assertEqual(plugin.layout_skill_dirs(design), {"a", "b"})

    def test_repo_skills(self):
        base = os.path.join(plugin.PLUGIN, "skills")
        dirs = sorted(d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d)))
        layout = plugin.layout_skill_dirs(plugin.read("DESIGN.md"))
        self.assertEqual(plugin.check_skill_dirs(dirs, layout), [])
        for d in dirs:
            self.assertEqual(plugin.check_skill(d, plugin.read("plugin", "skills", d, "SKILL.md")), [], d)


if __name__ == "__main__":
    unittest.main()
