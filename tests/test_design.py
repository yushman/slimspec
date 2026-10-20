import unittest

import plugin


def design(*nums):
    return "\n".join(f"### D{n}. t\nbody" for n in nums)


class DesignTest(unittest.TestCase):
    def test_flags_claude_range_differing_from_last_decision(self):
        problems = plugin.check_design_numbers(design(1, 2, 3), "decisions D1–D2.")
        self.assertTrue(any("D1–D2" in p for p in problems), problems)

    def test_flags_gap(self):
        self.assertTrue(plugin.check_design_numbers(design(1, 3), "D1–D3"))

    def test_flags_repeat(self):
        self.assertTrue(plugin.check_design_numbers(design(1, 2, 2), "D1–D2"))

    def test_flags_missing_range(self):
        self.assertTrue(plugin.check_design_numbers(design(1, 2), "no range"))

    def test_valid(self):
        self.assertEqual(plugin.check_design_numbers(design(1, 2, 3), "D1–D3"), [])

    def test_repo(self):
        self.assertEqual(plugin.check_design_numbers(plugin.read("DESIGN.md"), plugin.read("CLAUDE.md")), [])


if __name__ == "__main__":
    unittest.main()
