import importlib.util
import json
import os
import subprocess
import sys

SKIPPED = "skipped"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _events(text):
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except ValueError:
            return None
        if not isinstance(e, dict) or "type" not in e:
            return None
        out.append(e)
    return out or None


def is_stream_json(text):
    return _events(text) is not None


def _tool_uses(text):
    events = _events(text)
    if events is None:
        return SKIPPED
    uses = []
    for e in events:
        if e["type"] != "assistant":
            continue
        for block in (e.get("message") or {}).get("content") or []:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                uses.append((block.get("name"), block.get("input") or {}))
    return uses


def agent_launches(text):
    uses = _tool_uses(text)
    if uses == SKIPPED:
        return SKIPPED
    return [i.get("subagent_type") for n, i in uses if n in ("Agent", "Task")]


def tool_writes(text):
    uses = _tool_uses(text)
    if uses == SKIPPED:
        return SKIPPED
    writes = {}
    for name, inp in uses:
        if name == "Write":
            content = inp.get("content")
        elif name == "Edit":
            content = inp.get("new_string")
        else:
            continue
        writes.setdefault(inp.get("file_path"), []).append(content)
    return writes


def launched(text, agent, times=1):
    found = agent_launches(text)
    if found == SKIPPED:
        return SKIPPED
    return "pass" if found.count(agent) >= times else "fail"


def last_message(text):
    events = _events(text)
    if events is None:
        return text
    for e in reversed(events):
        if e["type"] == "result":
            return e.get("result", "")
    return ""


def changed_paths(sandbox):
    r = subprocess.run(["git", "status", "--porcelain", "-uall"], cwd=sandbox,
                       capture_output=True, text=True, check=True)
    return sorted(line[3:] for line in r.stdout.splitlines() if line)


def fixture_tests_pass(sandbox):
    r = subprocess.run([sys.executable, "-m", "unittest"], cwd=sandbox,
                       capture_output=True, text=True)
    return r.returncode == 0


def report(checks):
    print(json.dumps(checks))


def grammar():
    path = os.path.join(ROOT, "tests", "grammar.py")
    spec = importlib.util.spec_from_file_location("grammar", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
