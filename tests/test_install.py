import json
import os
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "install.sh"
ROLES = ["scanner", "debugger", "planner", "implementer", "reviewer", "grounder"]
CURL_STUB = """#!/bin/sh
echo "$@" >> "$CURL_LOG"
[ -z "${CURL_FAIL:-}" ] || exit 22
out=
while [ $# -gt 0 ]; do
  if [ "$1" = -o ]; then out=$2; shift; fi
  shift
done
cp "$CURL_TARBALL" "$out"
"""


def build_tarball(path):
    with tarfile.open(path, "w:gz") as tar:
        for d in ("plugin", "hosts"):
            tar.add(ROOT / d, arcname="slimspec-x/" + d,
                    filter=lambda i: None if "__pycache__" in i.name else i)


class InstallCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.tarball = Path(cls._tmp.name) / "src.tgz"
        build_tarball(cls.tarball)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        t = Path(self._t.name)
        self.home = t / "home"
        self.proj = t / "proj"
        self.bin = t / "bin"
        for d in (self.home, self.proj, self.bin):
            d.mkdir()
        curl = self.bin / "curl"
        curl.write_text(CURL_STUB)
        curl.chmod(0o755)
        self.log = t / "curl.log"
        self.log.write_text("")
        self.env = {
            "PATH": "%s:%s" % (self.bin, os.environ["PATH"]),
            "HOME": str(self.home),
            "CURL_LOG": str(self.log),
            "CURL_TARBALL": str(self.tarball),
        }

    def run_sh(self, *args, cwd=None, **env):
        e = dict(self.env, **env)
        return subprocess.run(["sh", str(SCRIPT), *args], cwd=cwd or self.proj,
                              env=e, capture_output=True, text=True)

    @property
    def data(self):
        return self.home / ".local/share/slimspec"

    @property
    def pdata(self):
        return self.proj / ".slimspec/install"

    def agent_files(self, d, ext):
        return [d / ("slimspec-%s.%s" % (r, ext)) for r in ROLES]


class TestInstall(InstallCase):
    def test_opencode_install_writes_five_agents_and_shared_stub(self):
        r = self.run_sh("opencode")
        self.assertEqual(r.returncode, 0, r.stderr)
        for d in ("skills", "agents"):
            self.assertTrue((self.data / d).is_dir())
        for m in ("opencode", "codex", "zcode"):
            self.assertTrue((self.data / "hosts" / (m + ".md")).is_file())
        for f in self.agent_files(self.home / ".config/opencode/agents", "md"):
            self.assertTrue(f.is_file(), f)
            self.assertNotIn("<root>", f.read_text())
            self.assertIn(str(self.data), f.read_text())
        stub = self.home / ".agents/skills/slimspec/SKILL.md"
        self.assertIn(str(self.data), stub.read_text())
        self.assertNotIn("<root>", stub.read_text())

    def test_zcode_install_writes_skill_and_agents(self):
        r = self.run_sh("zcode")
        self.assertEqual(r.returncode, 0, r.stderr)
        z = self.home / ".zcode"
        self.assertTrue((z / "skills/slimspec/SKILL.md").is_file())
        self.assertIn(str(self.data), (z / "skills/slimspec/SKILL.md").read_text())
        for f in self.agent_files(z / "agents", "md"):
            self.assertTrue(f.is_file(), f)
            self.assertNotIn("<root>", f.read_text())
        self.assertFalse((self.home / ".agents").exists())

    def test_codex_install_writes_toml_and_shared_stub(self):
        r = self.run_sh("codex")
        self.assertEqual(r.returncode, 0, r.stderr)
        for f in self.agent_files(self.home / ".codex/agents", "toml"):
            self.assertTrue(f.is_file(), f)
            self.assertNotIn("<root>", f.read_text())
        self.assertTrue((self.home / ".agents/skills/slimspec/SKILL.md").is_file())

    def test_all_installs_three_hosts_with_one_stub(self):
        r = self.run_sh("all")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.home / ".config/opencode/agents/slimspec-scanner.md").is_file())
        self.assertTrue((self.home / ".codex/agents/slimspec-scanner.toml").is_file())
        self.assertTrue((self.home / ".zcode/agents/slimspec-scanner.md").is_file())
        self.assertTrue((self.home / ".zcode/skills/slimspec/SKILL.md").is_file())
        self.assertEqual(len(list((self.home / ".agents/skills").iterdir())), 1)

    def test_xdg_data_home_is_honored(self):
        x = self.home / "xdg"
        r = self.run_sh("opencode", XDG_DATA_HOME=str(x))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((x / "slimspec/skills").is_dir())


class TestProject(InstallCase):
    def test_project_opencode_appends_gitignore_once(self):
        for _ in range(2):
            r = self.run_sh("opencode", "--project")
            self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.pdata / "skills").is_dir())
        for f in self.agent_files(self.proj / ".opencode/agents", "md"):
            self.assertIn(str(self.pdata), f.read_text())
        self.assertTrue((self.proj / ".agents/skills/slimspec/SKILL.md").is_file())
        lines = (self.proj / ".gitignore").read_text().splitlines()
        self.assertEqual(lines.count(".slimspec/install/"), 1)
        self.assertFalse((self.home / ".config").exists())

    def test_project_ignores_every_written_path_once_newline_safe(self):
        (self.proj / ".gitignore").write_text("node_modules")
        for _ in range(2):
            r = self.run_sh("all", "--project")
            self.assertEqual(r.returncode, 0, r.stderr)
        lines = (self.proj / ".gitignore").read_text().splitlines()
        self.assertEqual(lines[0], "node_modules")
        for p in (".slimspec/install/", ".agents/skills/slimspec/",
                  ".opencode/agents/slimspec-*", ".codex/agents/slimspec-*"):
            self.assertEqual(lines.count(p), 1, (p, lines))

    def test_project_codex_paths(self):
        r = self.run_sh("codex", "--project")
        self.assertEqual(r.returncode, 0, r.stderr)
        for f in self.agent_files(self.proj / ".codex/agents", "toml"):
            self.assertTrue(f.is_file(), f)

    def test_zcode_project_exits_2(self):
        r = self.run_sh("zcode", "--project")
        self.assertEqual(r.returncode, 2)
        self.assertFalse((self.proj / ".slimspec").exists())

    def test_all_project_skips_zcode_with_note(self):
        r = self.run_sh("all", "--project")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("zcode", r.stderr)
        self.assertTrue((self.proj / ".opencode/agents/slimspec-scanner.md").is_file())
        self.assertFalse((self.proj / ".zcode").exists())
        self.assertFalse((self.home / ".zcode").exists())


class TestErrors(InstallCase):
    def test_failed_download_leaves_no_files(self):
        r = self.run_sh("all", CURL_FAIL="1")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("archive/refs/tags/", self.log.read_text())
        self.assertNotIn("not found", r.stderr)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_failed_download_project_leaves_no_files(self):
        r = self.run_sh("opencode", "--project", CURL_FAIL="1")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("archive/refs/tags/", self.log.read_text())
        self.assertEqual(list(self.proj.iterdir()), [])

    def test_usage_errors_exit_2(self):
        for args in (["bogus"], [], ["opencode", "--bogus"], ["opencode", "--version"],
                     ["opencode", "codex"]):
            r = self.run_sh(*args)
            self.assertEqual(r.returncode, 2, args)
            self.assertIn("usage", r.stderr)
        self.assertEqual(self.log.read_text(), "")


class TestVersion(InstallCase):
    def test_version_line_equals_plugin_json(self):
        want = json.loads((ROOT / "plugin/.claude-plugin/plugin.json").read_text())["version"]
        lines = [l for l in SCRIPT.read_text().splitlines() if l.startswith("version=")]
        self.assertEqual(lines, ["version=" + want])

    def test_default_fetches_tag_of_version(self):
        want = json.loads((ROOT / "plugin/.claude-plugin/plugin.json").read_text())["version"]
        self.run_sh("opencode")
        self.assertIn("https://github.com/yushman/slimspec/archive/refs/tags/v%s.tar.gz" % want,
                      self.log.read_text())

    def test_version_flag_overrides_tag(self):
        self.run_sh("opencode", "--version", "v9.9.9")
        self.assertIn("/archive/refs/tags/v9.9.9.tar.gz", self.log.read_text())


class TestUninstall(InstallCase):
    def test_uninstall_codex_keeps_stub_while_opencode_remains(self):
        self.run_sh("all")
        r = self.run_sh("codex", "--uninstall")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse((self.home / ".codex/agents/slimspec-scanner.toml").exists())
        self.assertTrue((self.home / ".agents/skills/slimspec/SKILL.md").is_file())
        self.assertTrue(self.data.is_dir())

    def test_uninstall_last_agents_removes_stub_and_data(self):
        self.run_sh("opencode")
        self.run_sh("codex")
        self.run_sh("opencode", "--uninstall")
        self.assertTrue((self.home / ".agents/skills/slimspec").exists())
        self.run_sh("codex", "--uninstall")
        self.assertFalse((self.home / ".agents/skills/slimspec").exists())
        self.assertFalse(self.data.exists())

    def test_uninstall_keeps_data_while_zcode_remains(self):
        self.run_sh("all")
        self.run_sh("opencode", "--uninstall")
        self.run_sh("codex", "--uninstall")
        self.assertTrue(self.data.is_dir())
        self.assertTrue((self.home / ".zcode/agents/slimspec-scanner.md").is_file())
        self.run_sh("zcode", "--uninstall")
        self.assertFalse(self.data.exists())
        self.assertFalse((self.home / ".zcode/skills/slimspec").exists())

    def test_uninstall_keeps_foreign_files(self):
        self.run_sh("opencode")
        agents = self.home / ".config/opencode/agents"
        (agents / "mine.md").write_text("x")
        self.run_sh("opencode", "--uninstall")
        self.assertTrue((agents / "mine.md").is_file())
        self.assertFalse((agents / "slimspec-scanner.md").exists())

    def test_uninstall_keeps_foreign_shared_stub(self):
        stub = self.home / ".agents/skills/slimspec"
        stub.mkdir(parents=True)
        (stub / "SKILL.md").write_text("someone else's skill")
        r = self.run_sh("all", "--uninstall")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((stub / "SKILL.md").is_file())
        self.assertEqual((stub / "SKILL.md").read_text(), "someone else's skill")

    def test_uninstall_keeps_foreign_zcode_stub(self):
        stub = self.home / ".zcode/skills/slimspec"
        stub.mkdir(parents=True)
        (stub / "SKILL.md").write_text("someone else's skill")
        r = self.run_sh("zcode", "--uninstall")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual((stub / "SKILL.md").read_text(), "someone else's skill")

    def test_uninstall_drops_data_despite_foreign_zcode_stub(self):
        stub = self.home / ".zcode/skills/slimspec"
        stub.mkdir(parents=True)
        (stub / "SKILL.md").write_text("someone else's skill")
        self.run_sh("opencode")
        r = self.run_sh("opencode", "--uninstall")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(self.data.exists())
        self.assertEqual((stub / "SKILL.md").read_text(), "someone else's skill")

    def test_uninstall_project(self):
        self.run_sh("all", "--project")
        r = self.run_sh("all", "--project", "--uninstall")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(self.pdata.exists())
        self.assertFalse((self.proj / ".agents/skills/slimspec").exists())
        self.assertFalse((self.proj / ".opencode/agents/slimspec-scanner.md").exists())

    def test_uninstall_without_install_is_ok(self):
        r = self.run_sh("all", "--uninstall")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.log.read_text(), "")


if __name__ == "__main__":
    unittest.main()
