# Add mul to calc
mode: medium

## Goal
`calc.calc.mul(a, b)` returns the product of two numbers; a unit test in `tests/test_calc.py` covers it.

## Non-goals
- Division or any other operation.

## Decisions
### Where mul lives
- **Context:** calc has one module with `add`.
- **Choice:** add `mul` next to `add` in `calc/calc.py`.
- **Rejected:** a new module — one function does not need it.

## Risks
- None beyond a trivial function — accepted.
