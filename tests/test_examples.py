import glob
import os
import unittest

import grammar

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def example_problems(path, text):
    out = []
    for kind, problems in grammar.check_markdown(text):
        out += ["%s:%s" % (path, p.replace("line ", "", 1)) for p in problems]
    return out


class ExamplesTest(unittest.TestCase):
    def test_slimspec_examples_has_explore_and_both_tasks_blocks(self):
        path = os.path.join(ROOT, "skills", "slimspec", "examples.md")
        with open(path, encoding="utf-8") as f:
            kinds = [k for k, _ in grammar.check_markdown(f.read())]
        self.assertEqual(kinds.count("explore"), 1)
        self.assertEqual(kinds.count("tasks"), 2)

    def test_all_examples_pass_grammar(self):
        files = sorted(glob.glob(os.path.join(ROOT, "skills", "*", "examples.md")))
        self.assertTrue(files)
        problems = []
        for path in files:
            with open(path, encoding="utf-8") as f:
                problems += example_problems(os.path.relpath(path, ROOT), f.read())
        self.assertEqual(problems, [])

    def test_other_blocks_are_skipped(self):
        text = "```markdown\n# auth\n\n## Login\n- x\n```\n"
        self.assertEqual(grammar.check_markdown(text), [])

    def test_broken_copy_reported_with_file_and_line(self):
        path = os.path.join(ROOT, "skills", "slimspec", "examples.md")
        with open(path, encoding="utf-8") as f:
            text = f.read()
        broken = text.replace("## Risks", "## Dangers", 1)
        problems = example_problems("examples.md", broken)
        self.assertTrue(problems)
        self.assertRegex(problems[0], r"^examples\.md:\d+: ")


if __name__ == "__main__":
    unittest.main()
