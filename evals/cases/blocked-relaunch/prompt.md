Run /slimspec:apply with-tax. The change is planned in `.slimspec/changes/with-tax/`; the test command is `python3 -m unittest`. Commit mode: none, do not commit.

If an implementer reports a task BLOCKED, my answers are:
- Add `calc/rates.py` to the task's `files`, and let the task edit it.
- The rate is 20 percent: set `RATE = 20` in `calc/rates.py`, so `with_tax(100)` is 120.

Do not ask me anything else. After the answer, relaunch the implementer and finish the apply.
