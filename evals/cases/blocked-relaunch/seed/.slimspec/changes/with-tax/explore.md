# Add with_tax to calc
mode: medium

## Goal
`calc.calc.with_tax(amount)` returns the amount plus tax at the rate defined in `calc/rates.py`.

## Non-goals
- Rounding, currencies, per-item rates.

## Decisions
### Rate lives in calc/rates.py
- **Context:** the rate must be changeable without touching the arithmetic.
- **Choice:** `with_tax` reads `RATE` (percent) from `calc/rates.py`.
- **Rejected:** a function argument — callers would repeat the rate.

## Risks
- The rate value is not decided yet — accepted, to be settled when apply needs it.
