import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from bootstrap.sync import merge_file, sync_agents
from checks.review_budget import allowed_path, canonical_root, expected_remote, expected_refspec, pr_target


class SyncTests(unittest.TestCase):
    def merge(self, target, desired, name="settings"):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / f"{name}.json"
            path.write_text(json.dumps(target))
            merge_file(path, desired, name)
            first = path.read_bytes()
            merge_file(path, desired, name)
            self.assertEqual(first, path.read_bytes())
            return json.loads(first)

    def test_preserves_package_keys_and_is_idempotent(self):
        result = self.merge({"package": 1}, {"defaultProjectTrust": "always", "enableInstallTelemetry": False})
        self.assertEqual(result["package"], 1)

    def test_rejects_setting_drift(self):
        with self.assertRaisesRegex(ValueError, "conflict"):
            self.merge({"enableInstallTelemetry": True}, {"enableInstallTelemetry": False})

    def test_replace_failure_preserves_destination_and_removes_temporary_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            original = b'{"preserved": true}\n'
            path.write_bytes(original)
            with mock.patch("bootstrap.sync.os.replace", side_effect=OSError("replace failed")):
                with self.assertRaisesRegex(OSError, "replace failed"):
                    merge_file(path, {"added": True}, "settings")
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(list(Path(directory).iterdir()), [path])

    def test_preserves_engram_and_rejects_mcp_conflict(self):
        desired = {"mcpServers": {name: {"credentialRef": f"env:{name.upper()}"} for name in
                                  ("context7", "freecad", "gmail_emb", "gmail_personal", "gmail_zeler")}}
        result = self.merge({"mcpServers": {"engram": {"command": "engram"}}}, desired, "mcp")
        self.assertIn("engram", result["mcpServers"])
        self.assertEqual(len(result["mcpServers"]), 6)
        with self.assertRaises(ValueError):
            self.merge({"mcpServers": {"context7": {"command": "other"}}}, desired, "mcp")

    def test_preserves_existing_providers_and_updates_declared_model_provider(self):
        desired = {"providers": {"cliproxy": {"baseUrl": "http://127.0.0.1:8317/v1"}}}
        result = self.merge({"providers": {"openai": {"api": "openai-completions"}}}, desired, "models")
        self.assertIn("openai", result["providers"])
        self.assertEqual(result["providers"]["cliproxy"], desired["providers"]["cliproxy"])
        result = self.merge({"providers": {"cliproxy": {"baseUrl": "http://other"}}}, desired, "models")
        self.assertEqual(result["providers"]["cliproxy"], desired["providers"]["cliproxy"])

    def test_subagents_merge_preserves_package_agents_and_updates_declared_profiles(self):
        desired = {"model_profiles": {
            "sdd-design-high": {"model": "openai/gpt-5.6-sol", "effort": "medium"},
            "jd-fix-agent-high": {"model": "cliproxy/kimi-k2.7-code"},
        }}
        result = self.merge({"model_profiles": {"builtin-agent": {"model": "openai/gpt-5.6"}}}, desired, "subagents")
        self.assertIn("builtin-agent", result["model_profiles"])
        self.assertEqual(result["model_profiles"]["sdd-design-high"], desired["model_profiles"]["sdd-design-high"])
        result = self.merge({"model_profiles": {"sdd-design-high": {"model": "other"}}}, desired, "subagents")
        self.assertEqual(result["model_profiles"]["sdd-design-high"], desired["model_profiles"]["sdd-design-high"])

    def test_sync_agents_copies_only_markdown_without_deleting_foreign_files(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source"
            target = Path(directory) / "target"
            source.mkdir()
            target.mkdir()
            (source / "sdd-init-high.md").write_text("---\nname: sdd-init-high\n---")
            (source / "notes.txt").write_text("not an agent")
            (target / "package-owned.md").write_text("keep me")
            sync_agents(source, target)
            self.assertEqual((target / "sdd-init-high.md").read_text(), "---\nname: sdd-init-high\n---")
            self.assertFalse((target / "notes.txt").exists())
            self.assertEqual((target / "package-owned.md").read_text(), "keep me")

    def test_threat_guards_reject_unsafe_inputs(self):
        self.assertFalse(allowed_path("README.sh"))
        self.assertFalse(allowed_path("requirements.txt"))
        self.assertFalse(allowed_path("extra.bin"))
        self.assertFalse(allowed_path("config/pi/agents/evil.txt"))
        self.assertTrue(allowed_path("config/pi/agents/sdd-init-high.md", "pr3"))
        self.assertTrue(allowed_path("config/pi/subagents.user.json", "pr3"))
        self.assertFalse(canonical_root("/tmp/other", "/tmp/repo"))
        self.assertFalse(expected_remote("https://github.com/eduardoemb/other.git"))
        self.assertFalse(expected_refspec("origin/main:main"))
        self.assertFalse(pr_target("eduardoemb/other", "main", "feat/pi-bootstrap-core"))


if __name__ == "__main__":
    unittest.main()
