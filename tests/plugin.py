import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(ROOT, "plugin")


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    pairs = []
    for line in m.group(1).split("\n"):
        k, _, v = line.partition(":")
        pairs.append((k.strip(), v.strip()))
    return pairs


def design_tiers(design):
    m = re.search(r"### D16\..*?\n(.*?)\n###", design, re.S)
    return dict(re.findall(r"(\w+) — (\w+)", m.group(1)))


AGENT_KEYS = ["name", "description", "tools", "model"]


def check_agent(filename, text, tiers):
    fm = frontmatter(text)
    if fm is None:
        return [f"{filename}: no frontmatter"]
    problems = []
    keys = [k for k, _ in fm]
    if keys != AGENT_KEYS:
        problems.append(f"{filename}: frontmatter keys {keys}, expected {AGENT_KEYS}")
    d = dict(fm)
    role = filename[:-3] if filename.endswith(".md") else filename
    if d.get("name") != role:
        problems.append(f"{filename}: name {d.get('name')!r} != filename")
    if not d.get("description"):
        problems.append(f"{filename}: empty description")
    if not d.get("tools"):
        problems.append(f"{filename}: empty tools")
    if d.get("model") != tiers.get(role):
        problems.append(f"{filename}: model {d.get('model')!r} != D16 {tiers.get(role)!r}")
    return problems


def layout_skill_dirs(design):
    m = re.search(r"## Layout\n+```\n(.*?)\n```", design, re.S)
    block = m.group(1)
    sk = re.search(r"^    skills/\n(.*?)(?=^    \S|^  \S)", block + "\n  end", re.S | re.M)
    return set(re.findall(r"^      ([\w-]+)/", sk.group(1), re.M))


def check_skill_dirs(actual, layout):
    problems = [f"skills/{d} missing from DESIGN Layout" for d in sorted(set(actual) - layout)]
    problems += [f"DESIGN Layout lists skills/{d} but dir does not exist" for d in sorted(layout - set(actual))]
    return problems


def check_skill(dirname, text):
    fm = frontmatter(text)
    if fm is None:
        return [f"skills/{dirname}: no frontmatter"]
    d = dict(fm)
    problems = []
    if d.get("name") != dirname:
        problems.append(f"skills/{dirname}: name {d.get('name')!r} != dir name")
    if not d.get("description"):
        problems.append(f"skills/{dirname}: empty description")
    return problems


def md_files(*dirs):
    out = []
    for d in dirs:
        for base, _, names in os.walk(os.path.join(ROOT, d)):
            out += [os.path.join(base, n) for n in sorted(names) if n.endswith(".md")]
    return sorted(out)


def check_paths(path, text, root):
    problems = []
    rel = os.path.relpath(path, root)
    for n, line in enumerate(text.split("\n"), 1):
        for ref in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\s`'\")]*)", line):
            ref = ref.rstrip(".,;:")
            if "<" in ref:
                continue
            if not os.path.exists(os.path.join(root, ref)):
                problems.append(f"{rel}:{n}: unresolvable ${{CLAUDE_PLUGIN_ROOT}}/{ref}")
        for ref in re.findall(r"\]\(([^)\s]+)\)", line):
            ref = ref.split("#")[0]
            if not ref or "<" in ref or re.match(r"[a-z]+:", ref):
                continue
            if not os.path.exists(os.path.join(os.path.dirname(path), ref)):
                problems.append(f"{rel}:{n}: broken link {ref}")
    return problems


def check_agent_refs(path, text, agents, skill_dirs):
    problems = []
    rel = os.path.relpath(path, ROOT) if os.path.isabs(path) else path
    for n, line in enumerate(text.split("\n"), 1):
        for m in re.finditer(r"(?<![/\w])slimspec:([a-z-]+(?:\s*\|\s*[a-z-]+)*)", line):
            for name in re.split(r"\s*\|\s*", m.group(1)):
                if name not in skill_dirs and name not in agents:
                    problems.append(f"{rel}:{n}: slimspec:{name} has no agents/{name}.md")
    return problems


def check_design_numbers(design, claude):
    nums = [int(n) for n in re.findall(r"^### D(\d+)\.", design, re.M)]
    problems = []
    if nums != list(range(1, len(nums) + 1)):
        problems.append(f"DESIGN.md decisions not sequential from D1: {nums}")
    m = re.search(r"D1\u2013D(\d+)", claude)
    if not m:
        problems.append("CLAUDE.md has no D1\u2013Dn range")
    elif nums and int(m.group(1)) != max(nums):
        problems.append(f"CLAUDE.md range D1\u2013D{m.group(1)} != last DESIGN decision D{max(nums)}")
    return problems
