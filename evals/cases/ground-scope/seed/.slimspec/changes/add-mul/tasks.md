# Tasks: Add mul to calc
base: none
fix-cycles: 0

## Wave 1 (lane A: calc/*, tests/*)
Single lane: one function and its test in the same module.
- [x] T1 · lane: A · files: calc/calc.py, tests/test_calc.py · test-first: "mul multiplies two numbers" · done: mul(2, 3) returns 6
  evidence: red "test_mul — FAIL (ImportError: cannot import name mul)" · green "2 passed"
