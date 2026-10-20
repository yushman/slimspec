import json
import os
import sys


def judge(runs):
    names = []
    for run in runs:
        for name in run:
            if name not in names:
                names.append(name)
    result = {}
    for name in names:
        seen = [r[name] for r in runs if r.get(name) in ("pass", "fail")]
        passed = seen.count("pass")
        if not seen:
            result[name] = "skipped"
        elif name.startswith("hard-"):
            result[name] = "pass" if passed == len(seen) else "fail"
        else:
            result[name] = "pass" if passed * 2 > len(seen) else "fail"
    return result


def load(path):
    try:
        with open(path) as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
    except (OSError, ValueError):
        pass
    return {"hard-check-output": "fail"}


def main(results):
    ok = True
    ran = False
    for case in sorted(os.listdir(results)):
        cdir = os.path.join(results, case)
        if not os.path.isdir(cdir):
            continue
        names = sorted(os.listdir(cdir))
        if not names:
            continue
        ran = True
        runs = [load(os.path.join(cdir, r, "check.json"))
                for r in names]
        checks = judge(runs)
        passed = all(v != "fail" for v in checks.values())
        ok = ok and passed
        print(("PASS " if passed else "FAIL ") + case)
        for name, v in checks.items():
            print("  %s %s" % (v, name))
    if not ran:
        print("no cases ran")
        return 1
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
