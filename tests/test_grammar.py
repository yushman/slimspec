import unittest

import grammar

VALID_TASKS = """# Tasks: Demo
base: none
fix-cycles: 0

## Wave 1 (lane A: src/a/* · lane B: src/b/*)
Independent packages.
- [x] T1 · lane: A · files: src/a/x.py, src/a/test_x.py · test-first: "rejects expired" · done: 401 on expired
  evidence: red "rejects expired — FAIL (expected 401)" · green "4 passed"
  deviations: renamed validate
- [ ] T2 · lane: B · files: src/b/c.yaml · test: none — config only · check: build passes · done: flag readable

## Wave 2 (depends: T1 · lane A: src/api/*)
- [ ] T3 · fix: no 401 on refresh · lane: A · files: src/api/s.py · test-first: "refreshes" · done: no 401
"""

VALID_EXPLORE = """# Demo change
mode: medium

## Goal
Something observable.

## Non-goals
- nothing

## Decisions
### A choice
- **Context:** why
- **Choice:** what
- **Rejected:** other — no

## Risks
- risk — accepted
"""


class TasksTest(unittest.TestCase):
    def test_valid_document(self):
        self.assertEqual(grammar.parse_tasks(VALID_TASKS), [])

    def test_rejects_task_line_without_done(self):
        text = VALID_TASKS.replace(" · done: flag readable", "")
        problems = grammar.parse_tasks(text)
        self.assertTrue(any("done" in p for p in problems), problems)

    def test_missing_header(self):
        text = VALID_TASKS.replace("base: none\n", "")
        self.assertTrue(grammar.parse_tasks(text))

    def test_evidence_required_under_done(self):
        text = VALID_TASKS.replace(
            '  evidence: red "rejects expired — FAIL (expected 401)" · green "4 passed"\n', "")
        self.assertTrue(any("evidence" in p for p in grammar.parse_tasks(text)))

    def test_evidence_forbidden_under_open(self):
        text = VALID_TASKS.replace(
            "· done: flag readable\n", "· done: flag readable\n  evidence: red n/a — x · check \"ok\"\n")
        self.assertTrue(any("evidence" in p for p in grammar.parse_tasks(text)))

    def test_lane_not_in_heading(self):
        text = VALID_TASKS.replace("T2 · lane: B", "T2 · lane: C")
        self.assertTrue(any("lane" in p for p in grammar.parse_tasks(text)))

    def test_test_none_needs_check(self):
        text = VALID_TASKS.replace(" · check: build passes", "")
        self.assertTrue(any("check" in p for p in grammar.parse_tasks(text)))

    def test_invalidated_marker(self):
        text = VALID_TASKS.replace("T3 · fix: no 401 on refresh", "T3 · invalidated: numbers changed")
        self.assertEqual(grammar.parse_tasks(text), [])

    def test_bad_wave_heading(self):
        text = VALID_TASKS.replace("(lane A: src/a/* · lane B: src/b/*)", "(src/a/*)")
        self.assertTrue(grammar.parse_tasks(text))

    def test_problem_has_line_number(self):
        text = VALID_TASKS.replace(" · done: flag readable", "")
        self.assertIn("line 10:", " ".join(grammar.parse_tasks(text, first_line=1)))


class ExploreTest(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(grammar.parse_explore(VALID_EXPLORE), [])

    def test_rejects_without_mode_line(self):
        text = VALID_EXPLORE.replace("mode: medium\n", "")
        self.assertTrue(any("mode" in p for p in grammar.parse_explore(text)))

    def test_bad_mode_value(self):
        text = VALID_EXPLORE.replace("mode: medium", "mode: huge")
        self.assertTrue(any("mode" in p for p in grammar.parse_explore(text)))

    def test_section_order(self):
        text = VALID_EXPLORE.replace("## Goal", "## Tmp").replace("## Non-goals", "## Goal").replace("## Tmp", "## Non-goals")
        self.assertTrue(grammar.parse_explore(text))

    def test_decision_missing_rejected(self):
        text = VALID_EXPLORE.replace("- **Rejected:** other — no\n", "")
        self.assertTrue(any("Rejected" in p for p in grammar.parse_explore(text)))

    def test_tasks_section_validated(self):
        tasks = "\n## Tasks\n## Wave 1 (lane A: src/*)\n- [ ] T1 · lane: A · files: src/a.py · test-first: \"x\"\n"
        problems = grammar.parse_explore(VALID_EXPLORE + tasks)
        self.assertTrue(any("done" in p for p in problems), problems)
        ok = tasks.replace('"x"', '"x" · done: y')
        self.assertEqual(grammar.parse_explore(VALID_EXPLORE + ok), [])


if __name__ == "__main__":
    unittest.main()
