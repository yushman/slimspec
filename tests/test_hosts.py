import os
import re
import unittest

import plugin

ROLES = ["scanner", "debugger", "planner", "implementer", "reviewer", "grounder"]
READ_ONLY = ["scanner", "reviewer"]


def exists(*parts):
    return os.path.exists(os.path.join(plugin.ROOT, *parts))


def pointer_ok(role, body):
    return (
        f"<root>/agents/{role}.md" in body
        and "skip its frontmatter" in body
        and "`${CLAUDE_PLUGIN_ROOT}` there means `<root>`" in body
    )


def unquoted_colon_problems(role, fm):
    return [
        f"{role}: unquoted {k} contains ': '"
        for k, v in fm
        if ": " in v and v[0] not in "\"'"
    ]


def check_opencode_agent(role, text):
    if not exists("plugin", "agents", f"{role}.md"):
        return [f"{role}: no plugin agent"]
    fm = plugin.frontmatter(text)
    if fm is None:
        return [f"{role}: no frontmatter"]
    d = dict(fm)
    problems = unquoted_colon_problems(role, fm)
    if not d.get("description"):
        problems.append(f"{role}: no description")
    if d.get("mode") != "subagent":
        problems.append(f"{role}: mode must be subagent")
    for k in ("tools", "model"):
        if k in d:
            problems.append(f"{role}: {k} not allowed")
    if role in READ_ONLY and not re.search(r"permission:\n\s+edit: deny", text):
        problems.append(f"{role}: permission edit deny missing")
    body = text.split("\n---\n", 1)[-1]
    if not pointer_ok(role, body):
        problems.append(f"{role}: body does not point to the role file")
    return problems


def check_opencode_tree():
    problems = []
    for role in ROLES:
        rel = ("hosts", "opencode", "agents", f"slimspec-{role}.md")
        if not exists(*rel):
            problems.append(f"{'/'.join(rel)}: missing")
        else:
            problems += check_opencode_agent(role, plugin.read(*rel))
    return problems


GOOD_OPENCODE = """---
description: x
mode: subagent
permission:
  edit: deny
---

Read `<root>/agents/scanner.md`, skip its frontmatter, and follow it. `${CLAUDE_PLUGIN_ROOT}` there means `<root>`.
"""


class RolesTest(unittest.TestCase):
    def test_roles_match_plugin_agents(self):
        names = os.listdir(os.path.join(plugin.ROOT, "plugin", "agents"))
        self.assertEqual(sorted(ROLES), sorted(n[:-3] for n in names if n.endswith(".md")))


class OpenCodeAgentsTest(unittest.TestCase):
    def test_good_agent_passes(self):
        self.assertEqual(check_opencode_agent("scanner", GOOD_OPENCODE), [])

    def test_flags_missing_pointer_agent(self):
        self.assertEqual(check_opencode_agent("nosuchrole", GOOD_OPENCODE), ["nosuchrole: no plugin agent"])

    def test_flags_missing_mode(self):
        self.assertTrue(check_opencode_agent("scanner", GOOD_OPENCODE.replace("mode: subagent\n", "")))

    def test_flags_model_key(self):
        self.assertTrue(check_opencode_agent("scanner", GOOD_OPENCODE.replace("mode:", "model: x\nmode:")))

    def test_flags_read_only_without_edit_deny(self):
        text = GOOD_OPENCODE.replace("permission:\n  edit: deny\n", "")
        self.assertTrue(check_opencode_agent("scanner", text))

    def test_flags_body_without_pointer(self):
        text = GOOD_OPENCODE.replace("skip its frontmatter", "")
        self.assertTrue(check_opencode_agent("scanner", text))

    def test_flags_unquoted_colon_in_description(self):
        self.assertTrue(check_opencode_agent("scanner", GOOD_OPENCODE.replace("description: x", "description: a. b: c")))
        self.assertEqual(check_opencode_agent("scanner", GOOD_OPENCODE.replace("description: x", 'description: "a. b: c"')), [])

    def test_opencode_tree(self):
        self.assertEqual(check_opencode_tree(), [])


def toml_str(text, key):
    m = re.search(r'^' + key + r' = "((?:[^"\\]|\\.)*)"\s*$', text, re.M)
    return m.group(1) if m else None


def check_codex_agent(role, text):
    if not exists("plugin", "agents", f"{role}.md"):
        return [f"{role}: no plugin agent"]
    problems = []
    if toml_str(text, "name") != f"slimspec-{role}":
        problems.append(f"{role}: name must be slimspec-{role}")
    if not toml_str(text, "description"):
        problems.append(f"{role}: no description")
    m = re.search(r"^developer_instructions = '''\n(.*?)'''", text, re.S | re.M)
    if not m:
        return problems + [f"{role}: no developer_instructions"]
    for k in ("model", "sandbox_mode"):
        if re.search(r"^" + k + r"\s*=", text, re.M):
            problems.append(f"{role}: {k} not allowed")
    body = m.group(1)
    if not pointer_ok(role, body):
        problems.append(f"{role}: instructions do not point to the role file")
    if role in READ_ONLY and "never edit files" not in body.lower():
        problems.append(f"{role}: read-only role lacks 'never edit files'")
    return problems


def check_codex_tree():
    problems = []
    for role in ROLES:
        rel = ("hosts", "codex", "agents", f"slimspec-{role}.toml")
        if not exists(*rel):
            problems.append(f"{'/'.join(rel)}: missing")
        else:
            problems += check_codex_agent(role, plugin.read(*rel))
    return problems


GOOD_CODEX = (
    'name = "slimspec-scanner"\n'
    'description = "x"\n'
    "developer_instructions = '''\n"
    "Read `<root>/agents/scanner.md`, skip its frontmatter, and follow it. "
    "`${CLAUDE_PLUGIN_ROOT}` there means `<root>`. Never edit files.\n"
    "'''\n"
)


class CodexAgentsTest(unittest.TestCase):
    def test_good_agent_passes(self):
        self.assertEqual(check_codex_agent("scanner", GOOD_CODEX), [])

    def test_flags_missing_developer_instructions(self):
        text = GOOD_CODEX.split("developer_instructions")[0]
        self.assertEqual(check_codex_agent("scanner", text), ["scanner: no developer_instructions"])

    def test_flags_basic_multiline_string(self):
        self.assertTrue(check_codex_agent("scanner", GOOD_CODEX.replace("'''", '"""')))

    def test_flags_wrong_name(self):
        self.assertTrue(check_codex_agent("scanner", GOOD_CODEX.replace("slimspec-scanner", "scanner")))

    def test_flags_missing_description(self):
        self.assertTrue(check_codex_agent("scanner", GOOD_CODEX.replace('description = "x"\n', "")))

    def test_flags_model_and_sandbox(self):
        self.assertTrue(check_codex_agent("scanner", 'model = "x"\n' + GOOD_CODEX))
        self.assertTrue(check_codex_agent("scanner", 'sandbox_mode = "read-only"\n' + GOOD_CODEX))

    def test_flags_read_only_without_never_edit(self):
        self.assertTrue(check_codex_agent("scanner", GOOD_CODEX.replace("Never edit files.", "")))

    def test_flags_missing_role_file(self):
        self.assertTrue(check_codex_agent("nosuchrole", GOOD_CODEX))

    def test_codex_tree(self):
        self.assertEqual(check_codex_tree(), [])


def check_zcode_agent(role, text):
    if not exists("plugin", "agents", f"{role}.md"):
        return [f"{role}: no plugin agent"]
    fm = plugin.frontmatter(text)
    if fm is None:
        return [f"{role}: no frontmatter"]
    d = dict(fm)
    problems = unquoted_colon_problems(role, fm)
    if d.get("name") != f"slimspec-{role}":
        problems.append(f"{role}: name must be slimspec-{role}")
    if not d.get("description"):
        problems.append(f"{role}: no description")
    if "model" in d:
        problems.append(f"{role}: model not allowed")
    if role in READ_ONLY:
        denied = re.split(r"[,\s]+", d.get("disallowedTools", ""))
        if not {"Edit", "Write"} <= set(denied):
            problems.append(f"{role}: disallowedTools must name Edit and Write")
    body = text.split("\n---\n", 1)[-1]
    if not pointer_ok(role, body):
        problems.append(f"{role}: body does not point to the role file")
    return problems


def check_zcode_tree():
    problems = []
    for role in ROLES:
        rel = ("hosts", "zcode", "agents", f"slimspec-{role}.md")
        if not exists(*rel):
            problems.append(f"{'/'.join(rel)}: missing")
        else:
            problems += check_zcode_agent(role, plugin.read(*rel))
    return problems


GOOD_ZCODE = """---
name: slimspec-scanner
description: x
disallowedTools: Edit, Write
---

Read `<root>/agents/scanner.md`, skip its frontmatter, and follow it. `${CLAUDE_PLUGIN_ROOT}` there means `<root>`.
"""


class ZCodeAgentsTest(unittest.TestCase):
    def test_good_agent_passes(self):
        self.assertEqual(check_zcode_agent("scanner", GOOD_ZCODE), [])

    def test_flags_read_only_without_disallowed_edit_write(self):
        self.assertTrue(check_zcode_agent("scanner", GOOD_ZCODE.replace("disallowedTools: Edit, Write\n", "")))
        self.assertTrue(check_zcode_agent("scanner", GOOD_ZCODE.replace("Edit, Write", "Edit")))

    def test_flags_wrong_name(self):
        self.assertTrue(check_zcode_agent("scanner", GOOD_ZCODE.replace("slimspec-scanner", "scanner")))

    def test_flags_empty_description(self):
        self.assertTrue(check_zcode_agent("scanner", GOOD_ZCODE.replace("description: x", "description:")))

    def test_flags_model_key(self):
        self.assertTrue(check_zcode_agent("scanner", GOOD_ZCODE.replace("description:", "model: x\ndescription:")))

    def test_flags_missing_role_file(self):
        self.assertTrue(check_zcode_agent("nosuchrole", GOOD_ZCODE))

    def test_flags_unquoted_colon_in_description(self):
        self.assertTrue(check_zcode_agent("scanner", GOOD_ZCODE.replace("description: x", "description: a. b: c")))
        self.assertEqual(check_zcode_agent("scanner", GOOD_ZCODE.replace("description: x", 'description: "a. b: c"')), [])

    def test_zcode_tree(self):
        self.assertEqual(check_zcode_tree(), [])


STUB_REFS = [
    "<root>/hosts/opencode.md",
    "<root>/hosts/codex.md",
    "<root>/hosts/zcode.md",
    "<root>/skills/slimspec/SKILL.md",
    "<root>/skills/<",
]


def check_stub(text):
    fm = plugin.frontmatter(text)
    if fm is None:
        return ["stub: no frontmatter"]
    d = dict(fm)
    problems = []
    if d.get("name") != "slimspec":
        problems.append("stub: name must be slimspec")
    if not d.get("description"):
        problems.append("stub: no description")
    problems += [f"stub: does not name {r}" for r in STUB_REFS if r not in text]
    return problems


GOOD_STUB = "---\nname: slimspec\ndescription: x\n---\n\n" + "\n".join(STUB_REFS) + "\n"


class StubTest(unittest.TestCase):
    def test_good_stub_passes(self):
        self.assertEqual(check_stub(GOOD_STUB), [])

    def test_flags_stub_without_zcode_mapping(self):
        self.assertEqual(
            check_stub(GOOD_STUB.replace("<root>/hosts/zcode.md", "")),
            ["stub: does not name <root>/hosts/zcode.md"],
        )

    def test_flags_wrong_name_and_empty_description(self):
        self.assertEqual(len(check_stub(GOOD_STUB.replace("name: slimspec", "name: x").replace("description: x", "description:"))), 2)

    def test_flags_missing_frontmatter(self):
        self.assertEqual(check_stub("no frontmatter"), ["stub: no frontmatter"])

    def test_repo_stub(self):
        self.assertTrue(exists("hosts", "skill", "SKILL.md"))
        self.assertEqual(check_stub(plugin.read("hosts", "skill", "SKILL.md")), [])


class MappingFilesTest(unittest.TestCase):
    def test_mapping_files_exist(self):
        for host in ("opencode", "codex", "zcode"):
            self.assertTrue(exists("hosts", f"{host}.md"), f"hosts/{host}.md missing")

    def test_mappings_name_config_yaml_and_init_agents_md(self):
        for host in ("opencode", "codex", "zcode"):
            text = plugin.read("hosts", f"{host}.md")
            self.assertIn(".slimspec/config.yaml", text, host)
            self.assertNotIn("config.yml", text, host)
            self.assertRegex(text, r"`init`[^\n]*`agents-md` first", host)

    def test_init_options_and_batching_are_explicit(self):
        options = "`agents-md` (recommended) | `claude-md` | `readme` | `central`"
        for host in ("opencode", "codex", "zcode"):
            text = plugin.read("hosts", f"{host}.md")
            self.assertIn(options, text, host)
            self.assertRegex(text, r"`native`[^\n]*`none`", host)
            self.assertIn("up to 4 independent questions", text, host)

    def test_no_one_decision_per_call(self):
        for host in ("opencode", "codex", "zcode"):
            self.assertNotIn("one decision per call", plugin.read("hosts", f"{host}.md"), host)

    def test_opencode_batches_in_one_question_call(self):
        self.assertIn("one `question` call", plugin.read("hosts", "opencode.md"))


if __name__ == "__main__":
    unittest.main()
