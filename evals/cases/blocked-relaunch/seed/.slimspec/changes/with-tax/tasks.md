# Tasks: Add with_tax to calc
base: none
fix-cycles: 0

## Wave 1 (lane A: calc/calc.py, tests/test_calc.py)
One lane: a single task.
- [ ] T1 · lane: A · files: calc/calc.py, tests/test_calc.py · test-first: "with_tax adds tax at the configured rate" · done: with_tax(100) returns 100 plus the percent RATE from calc/rates.py, and RATE holds the agreed rate
