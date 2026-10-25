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
