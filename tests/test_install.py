"""Exercise public installation boundaries in an isolated home directory."""

from pathlib import Path
import subprocess
import tempfile
import unittest
import os


ROOT = Path(__file__).resolve().parents[1]


class InstallTests(unittest.TestCase):
    """Keep source assets intact and local-only data out of installations."""

    def test_install_prune_and_uninstall(self):
        """Check bytes, notices, dry-run, pruning, and unmanaged-file preservation."""
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            target = home / ".agents"
            env = {**os.environ, "HOME": directory}

            def install(*flags):
                subprocess.run(
                    [str(ROOT / "scripts/install.sh"), "--target", "agents", *flags],
                    cwd=ROOT,
                    env=env,
                    input="",
                    text=True,
                    check=True,
                    capture_output=True,
                )

            install("--dry-run")
            self.assertFalse(target.exists())
            install()
            mapping = {"agents.md": "agents.kit.md"}
            for folder in ("skills", "agents", "rules"):
                for source in (ROOT / folder).rglob("*"):
                    if not source.is_file() or source.name == ".DS_Store" or "node_modules" in source.parts:
                        continue
                    relative = source.relative_to(ROOT)
                    destination = relative.with_name("skill.md") if source.name == "SKILL.md" else relative
                    mapping[str(destination)] = str(relative)
                    if source.name == "SKILL.md":
                        mapping[str(relative)] = str(relative)
            mapping.update({name: name for name in ("LICENSE", "THIRD-PARTY-NOTICES.md")})
            for destination, source in mapping.items():
                with self.subTest(source=source):
                    self.assertEqual((ROOT / source).read_bytes(), (target / destination).read_bytes())
                    if os.access(ROOT / source, os.X_OK):
                        self.assertTrue(os.access(target / destination, os.X_OK))
            stamped = set((target / ".kit-stamp").read_text().splitlines()[2:])
            self.assertEqual(set(mapping), stamped)
            retired = [
                f"agents/cr-{name}" for name in (
                    "architecture", "correctness", "deployment-safety", "implementer",
                    "organization", "performance", "planner", "security",
                    "simplification", "test-quality", "verifier",
                )
            ]
            retired += [
                f"rules/{name}.md" for name in (
                    "code-organization", "comment-style", "git-worktrees",
                    "minimal-changes", "subagents", "writing-voice",
                )
            ]
            retired += ["skills/code-review", "skills/research"]
            for missing in retired:
                self.assertFalse((ROOT / missing).exists(), missing)
            for missing in ["skills-disabled", "scripts", *retired]:
                self.assertFalse((target / missing).exists(), missing)
            # The two skill filename spellings share an inode on case-insensitive homes.
            installed = {((target / name).stat().st_dev, (target / name).stat().st_ino) for name in mapping}
            self.assertEqual(len(installed) + 1, sum(path.is_file() for path in target.rglob("*")))

            bin_dir = home / "bin"
            bin_dir.mkdir()
            dot = bin_dir / "dot"
            dot.write_text("#!/bin/sh\nexit 0\n")
            dot.chmod(0o755)
            subprocess.run(
                ["node", str(target / "skills/writing-skills/render-graphs.js"), str(target / "skills/writing-skills")],
                env={**env, "PATH": f"{bin_dir}{os.pathsep}{env['PATH']}"},
                text=True,
                check=True,
                capture_output=True,
            )

            unmanaged = target / "local-only.txt"
            unmanaged.write_text("keep this file\n")
            obsolete = target / "retired-managed.txt"
            obsolete.write_text("retired content\n")
            with (target / ".kit-stamp").open("a") as stamp:
                stamp.write("retired-managed.txt\n")
            install("--prune", "--dry-run")
            self.assertTrue(obsolete.exists())
            install("--prune")
            self.assertFalse(obsolete.exists())
            self.assertTrue(unmanaged.exists())
            install("--uninstall")
            self.assertEqual([unmanaged], [path for path in target.rglob("*") if path.is_file()])


if __name__ == "__main__":
    unittest.main()
