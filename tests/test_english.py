import os
import re
import unittest

import plugin

CYRILLIC = re.compile("[Ѐ-ӿ]")


def find_cyrillic(path, text):
    return [f"{path}:{n}: Cyrillic" for n, line in enumerate(text.split("\n"), 1) if CYRILLIC.search(line)]


def prompt_files():
    out = []
    for d in ("skills", "agents"):
        for base, _, names in os.walk(os.path.join(plugin.ROOT, d)):
            out += [os.path.join(base, n) for n in names if n.endswith(".md")]
    return sorted(out) + [os.path.join(plugin.ROOT, f) for f in ("DESIGN.md", "CLAUDE.md")]


class EnglishTest(unittest.TestCase):
    def test_flags_cyrillic_in_skills_file(self):
        problems = find_cyrillic("skills/x/SKILL.md", "fine\nпривет\n")
        self.assertEqual(problems, ["skills/x/SKILL.md:2: Cyrillic"])

    def test_no_cyrillic_in_plain_english(self):
        self.assertEqual(find_cyrillic("a.md", "hello — world"), [])

    def test_repo_is_english(self):
        problems = []
        for f in prompt_files():
            with open(f, encoding="utf-8") as fh:
                problems += find_cyrillic(os.path.relpath(f, plugin.ROOT), fh.read())
        self.assertEqual(problems, [])


if __name__ == "__main__":
    unittest.main()
