"""Verify verbatim GLM payloads in the kit and its installed skill.

Expected SHA-256 values were calculated before implementation from git show
5905904e02de887dde3d4de3d7b83313ffc38c5e:<path> in glm-5.3-flash-drafter.
coding.md and domain.md use the entire docs/agents/<name> blob.
For agent-rules.txt, split AGENTS.md bytes with splitlines(keepends=True),
then concatenate b"".join(lines[5:23]) + b"\n" + b"".join(lines[55:73]).
For issue-tracker-evidence.txt, split docs/agents/issue-tracker.md the same
way, then concatenate b"".join(lines[42:49]). No decoding or newline
normalization is applied; terminal newlines are included in the hashes.
"""

import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = Path("skills/setup-repository/templates")
EXPECTED_SHA256 = {
    "coding.txt": "e583fe3c0b1cb25be5b3dafdc6b0fe94c9b8e3c9bdbfdc2f9b87d1728111ae7c",
    "domain.txt": "4f9c0172770fcad1374ec7bfee22502a06f0f61d52ae741d30fb8862ed087cf2",
    "agent-rules.txt": "7731c884c94de49adcf30b337f3ab33a010e0b280cd4910f7b9ff06ae5213e21",
    "issue-tracker-evidence.txt": "564cf08b9274732fd74db87d66dd4b4260fe4b8be6c72f93b9dcbc15633c2f5d",
}


class SetupRepositoryPayloadTests(unittest.TestCase):
    """Check each payload independently against a pinned external source."""

    def assert_payload_hashes(self, directory):
        """Report every missing or altered payload, including newline changes."""
        for name, expected in EXPECTED_SHA256.items():
            with self.subTest(payload=name):
                path = directory / name
                self.assertTrue(path.is_file(), f"Missing payload: {path}")
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected)

    def test_packaged_payloads_match_pinned_source(self):
        """The distributed templates preserve the authoritative source bytes."""
        self.assert_payload_hashes(REPO_ROOT / TEMPLATES)

    def test_installer_preserves_all_payloads(self):
        """A real noninteractive install delivers every literal rule payload."""
        with tempfile.TemporaryDirectory(prefix="setup-repository-home-") as home:
            result = subprocess.run(
                ["bash", "scripts/install.sh", "--target", "agents"],
                cwd=REPO_ROOT,
                env={**os.environ, "HOME": home, "TMPDIR": home},
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
            with self.subTest(installer="exit status"):
                self.assertEqual(
                    result.returncode, 0, f"{result.stdout}\n{result.stderr}"
                )
            self.assert_payload_hashes(Path(home) / ".agents" / TEMPLATES)


class InstallRulesCliTests(unittest.TestCase):
    """Test deterministic preflight and installation helper behavior."""

    def setUp(self):
        self.script = REPO_ROOT / "skills" / "setup-repository" / "install_rules.py"

    def run_cli(self, *args, cwd=None):
        return subprocess.run(
            [sys.executable, str(self.script), *args],
            cwd=cwd or REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_fresh_install_and_link_resolution(self):
        """Fresh install writes all destinations and satisfies coding link targets."""
        with tempfile.TemporaryDirectory() as target_dir:
            target = Path(target_dir)
            check_res = self.run_cli("--check", target_dir)
            self.assertEqual(check_res.returncode, 0, check_res.stderr)
            self.assertIn("[CREATE] docs/agents/coding.md", check_res.stdout)

            apply_res = self.run_cli("--apply", target_dir)
            self.assertEqual(apply_res.returncode, 0, apply_res.stderr)
            self.assertTrue((target / "docs" / "agents" / "coding.md").is_file())
            self.assertTrue((target / "docs" / "agents" / "domain.md").is_file())
            self.assertTrue((target / "AGENTS.md").is_file())
            self.assertTrue((target / "docs" / "agents" / "issue-tracker.md").is_file())

            # Repeat run is byte-idempotent
            repeat_res = self.run_cli("--check", target_dir)
            self.assertEqual(repeat_res.returncode, 0, repeat_res.stderr)
            self.assertIn("[NOOP] docs/agents/coding.md", repeat_res.stdout)
            self.assertIn("[PRESERVE] docs/agents/domain.md", repeat_res.stdout)

    def test_domain_preservation_and_lowercase_agents_resolution(self):
        """Preserves existing domain guide and updates existing lowercase agents.md."""
        with tempfile.TemporaryDirectory() as target_dir:
            target = Path(target_dir)
            (target / "docs" / "agents").mkdir(parents=True)
            custom_domain = target / "docs" / "agents" / "domain.md"
            custom_domain.write_text("Custom Project Domain Guide\n", encoding="utf-8")

            lower_agents = target / "agents.md"
            lower_agents.write_text("# Project Instructions\n\nIntro text.\n", encoding="utf-8")

            apply_res = self.run_cli("--apply", target_dir)
            self.assertEqual(apply_res.returncode, 0, apply_res.stderr)
            self.assertEqual(custom_domain.read_text(encoding="utf-8"), "Custom Project Domain Guide\n")
            filenames = [p.name for p in target.iterdir()]
            self.assertIn("agents.md", filenames)
            self.assertNotIn("AGENTS.md", filenames)
            self.assertIn("<!-- setup-repository:agent-rules:start -->", lower_agents.read_text(encoding="utf-8"))

    def test_conflict_detection_and_approval(self):
        """Differing managed block triggers conflict on check and requires approval."""
        with tempfile.TemporaryDirectory() as target_dir:
            target = Path(target_dir)
            self.run_cli("--apply", target_dir)

            # Introduce conflict into AGENTS.md
            agents_file = target / "AGENTS.md"
            content = agents_file.read_text(encoding="utf-8")
            s = "<!-- setup-repository:agent-rules:start -->\n"
            e = "<!-- setup-repository:agent-rules:end -->"
            pre, rest = content.split(s, 1)
            _, post = rest.split(e, 1)
            agents_file.write_text(f"{pre}{s}altered block\n{e}{post}", encoding="utf-8")

            # Check detects conflict
            check_res = self.run_cli("--check", target_dir)
            self.assertEqual(check_res.returncode, 1)
            self.assertIn("[CONFLICT] AGENTS.md", check_res.stdout)

            # Apply without approval fails
            fail_apply = self.run_cli("--apply", target_dir)
            self.assertEqual(fail_apply.returncode, 1)

            # Apply with approval succeeds
            ok_apply = self.run_cli("--apply", target_dir, "--approve-conflicts")
            self.assertEqual(ok_apply.returncode, 0, ok_apply.stderr)

    def test_malformed_marker_rejection(self):
        """Malformed marker blocks check and apply."""
        with tempfile.TemporaryDirectory() as target_dir:
            target = Path(target_dir)
            agents_file = target / "AGENTS.md"
            agents_file.write_text("<!-- setup-repository:agent-rules:start -->\nOnly start marker\n", encoding="utf-8")

            check_res = self.run_cli("--check", target_dir)
            self.assertEqual(check_res.returncode, 2)
            apply_res = self.run_cli("--apply", target_dir)
            self.assertEqual(apply_res.returncode, 2)
