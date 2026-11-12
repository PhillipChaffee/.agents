#!/usr/bin/env python3
"""Deterministic preflight and installation helper for repository working rules.

Installs maintained rule payloads verbatim, managing whole files and marked blocks.
Never alters payload bytes. Preserves existing domain guides and file prefixes/suffixes.
"""

from __future__ import annotations

import argparse
import difflib
from pathlib import Path
import sys

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

PAYLOAD_FILES = {
    "coding": "coding.txt",
    "domain": "domain.txt",
    "agent_rules": "agent-rules.txt",
    "issue_tracker_evidence": "issue-tracker-evidence.txt",
}

MARKERS = {
    "agent_rules": (
        "<!-- setup-repository:agent-rules:start -->",
        "<!-- setup-repository:agent-rules:end -->",
    ),
    "issue_tracker_evidence": (
        "<!-- setup-repository:issue-tracker-evidence:start -->",
        "<!-- setup-repository:issue-tracker-evidence:end -->",
    ),
}

UNMANAGED_HEADINGS = {
    "agent_rules": [
        "## Required terminology and naming",
        "## Working rules",
        "## Evidence",
        "## Comments",
        "## Human-facing writing",
    ],
    "issue_tracker_evidence": [
        "## Evidence and completion",
    ],
}


def load_payloads(templates_dir: Path = TEMPLATES_DIR) -> dict[str, bytes]:
    """Read all required rule payloads as exact bytes."""
    return {k: (templates_dir / f).read_bytes() for k, f in PAYLOAD_FILES.items()}


def resolve_root_instructions(target_repo: Path) -> Path:
    """Find root instructions file case-insensitively, preserving exact directory entry casing."""
    if target_repo.is_dir():
        for entry in target_repo.iterdir():
            if entry.name.lower() == "agents.md":
                return entry
    return target_repo / "AGENTS.md"


def extract_block(text: str, start_marker: str, end_marker: str) -> tuple[str, str, str] | None:
    """Extract content inside markers, returning (prefix, block_content, suffix)."""
    start_count = text.count(start_marker)
    end_count = text.count(end_marker)
    if start_count == 0 and end_count == 0:
        return None
    if start_count != 1 or end_count != 1:
        raise ValueError("Malformed or duplicate markers found")
    start_idx = text.find(start_marker)
    end_idx = text.find(end_marker)
    if end_idx < start_idx:
        raise ValueError("End marker occurs before start marker")
    start_line_end = text.find("\n", start_idx)
    if start_line_end == -1 or start_line_end >= end_idx:
        raise ValueError("Malformed start marker line")
    end_line_end = text.find("\n", end_idx)
    end_after = end_line_end + 1 if end_line_end != -1 else len(text)
    return text[:start_idx], text[start_line_end + 1:end_idx], text[end_after:]


def format_block(payload_text: str, start_marker: str, end_marker: str) -> str:
    """Assemble a marked block with standard delimiters."""
    block = f"{start_marker}\n{payload_text}"
    if not block.endswith("\n"):
        block += "\n"
    return f"{block}{end_marker}\n"


class DestinationCheck:
    def __init__(
        self,
        key: str,
        rel_path: str,
        status: str,
        message: str = "",
        diff: str = "",
        target_path: Path | None = None,
        write_content: str | bytes | None = None,
    ):
        self.key = key
        self.rel_path = rel_path
        self.status = status  # CREATE, NOOP, PRESERVE, APPEND, CONFLICT, MALFORMED_MARKER
        self.message = message
        self.diff = diff
        self.target_path = target_path
        self.write_content = write_content


def check_whole_file(rel: str, path: Path, payload: bytes, preserve_existing: bool = False) -> DestinationCheck:
    if not path.exists():
        return DestinationCheck(rel, rel, "CREATE", target_path=path, write_content=payload)
    if preserve_existing:
        return DestinationCheck(rel, rel, "PRESERVE", message="Preserving existing guide", target_path=path)
    cur = path.read_bytes()
    if cur == payload:
        return DestinationCheck(rel, rel, "NOOP", target_path=path)
    diff = "".join(
        difflib.unified_diff(
            cur.decode("utf-8", errors="replace").splitlines(keepends=True),
            payload.decode("utf-8").splitlines(keepends=True),
            fromfile=f"{rel} (existing)",
            tofile=f"{rel} (payload)",
        )
    )
    return DestinationCheck(rel, rel, "CONFLICT", message="Content differs from payload", diff=diff, target_path=path, write_content=payload)


def check_marked_block(
    key: str, rel: str, path: Path, payload: bytes, header_title: str, markers: tuple[str, str], headings: list[str]
) -> DestinationCheck:
    start_m, end_m = markers
    payload_txt = payload.decode("utf-8")
    block_txt = format_block(payload_txt, start_m, end_m)
    if not path.exists():
        return DestinationCheck(key, rel, "CREATE", target_path=path, write_content=f"# {header_title}\n\n{block_txt}")
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        extracted = extract_block(text, start_m, end_m)
    except ValueError as err:
        return DestinationCheck(key, rel, "MALFORMED_MARKER", message=str(err), target_path=path)
    if extracted is not None:
        pfx, cur_blk, sfx = extracted
        if cur_blk == payload_txt:
            return DestinationCheck(key, rel, "NOOP", target_path=path)
        diff = "".join(
            difflib.unified_diff(
                cur_blk.splitlines(keepends=True),
                payload_txt.splitlines(keepends=True),
                fromfile=f"{rel} (existing block)",
                tofile=f"{rel} (payload block)",
            )
        )
        return DestinationCheck(
            key, rel, "CONFLICT", message="Managed block differs", diff=diff, target_path=path, write_content=f"{pfx}{block_txt}{sfx}"
        )
    collisions = [h for h in headings if h in text]
    sep = "" if text.endswith("\n\n") else ("\n" if text.endswith("\n") else "\n\n")
    new_full = f"{text}{sep}{block_txt}"
    if collisions:
        return DestinationCheck(key, rel, "CONFLICT", message=f"Colliding headings: {', '.join(collisions)}", target_path=path, write_content=new_full)
    return DestinationCheck(key, rel, "APPEND", target_path=path, write_content=new_full)


def inspect_destinations(target_repo: Path, payloads: dict[str, bytes]) -> list[DestinationCheck]:
    agents_path = resolve_root_instructions(target_repo)
    rel_agents = agents_path.relative_to(target_repo).as_posix()
    return [
        check_whole_file("docs/agents/coding.md", target_repo / "docs/agents/coding.md", payloads["coding"]),
        check_whole_file("docs/agents/domain.md", target_repo / "docs/agents/domain.md", payloads["domain"], preserve_existing=True),
        check_marked_block(
            "agent_rules", rel_agents, agents_path, payloads["agent_rules"], "Agent guidelines", MARKERS["agent_rules"], UNMANAGED_HEADINGS["agent_rules"]
        ),
        check_marked_block(
            "issue_tracker_evidence",
            "docs/agents/issue-tracker.md",
            target_repo / "docs/agents/issue-tracker.md",
            payloads["issue_tracker_evidence"],
            "Issue tracker",
            MARKERS["issue_tracker_evidence"],
            UNMANAGED_HEADINGS["issue_tracker_evidence"],
        ),
    ]


def verify_installed(target_repo: Path, payloads: dict[str, bytes]) -> list[str]:
    errors: list[str] = []
    coding_path = target_repo / "docs/agents/coding.md"
    if not coding_path.is_file() or coding_path.read_bytes() != payloads["coding"]:
        errors.append("docs/agents/coding.md does not match payload")
    if not (target_repo / "docs/agents/domain.md").is_file():
        errors.append("docs/agents/domain.md missing")
    agents_path = resolve_root_instructions(target_repo)
    if not agents_path.is_file():
        errors.append(f"{agents_path.name} missing")
    else:
        ext = extract_block(agents_path.read_text(encoding="utf-8", errors="replace"), *MARKERS["agent_rules"])
        if not ext or ext[1] != payloads["agent_rules"].decode("utf-8"):
            errors.append(f"{agents_path.name} block does not match payload")
    tracker_path = target_repo / "docs/agents/issue-tracker.md"
    if not tracker_path.is_file():
        errors.append("docs/agents/issue-tracker.md missing")
    else:
        text = tracker_path.read_text(encoding="utf-8", errors="replace")
        ext = extract_block(text, *MARKERS["issue_tracker_evidence"])
        if not ext or ext[1] != payloads["issue_tracker_evidence"].decode("utf-8"):
            errors.append("docs/agents/issue-tracker.md block does not match payload")
        if "## Evidence and completion" not in text:
            errors.append("docs/agents/issue-tracker.md missing heading anchor")
    return errors


def run_check(target_repo: Path, payloads: dict[str, bytes]) -> int:
    checks = inspect_destinations(target_repo, payloads)
    has_conflict = False
    has_malformed = False
    print(f"Preflight inspection: {target_repo}")
    for c in checks:
        msg = f" ({c.message})" if c.message else ""
        print(f"  [{c.status}] {c.rel_path}{msg}")
        if c.diff:
            print("\n" + c.diff)
        if c.status == "CONFLICT":
            has_conflict = True
        elif c.status == "MALFORMED_MARKER":
            has_malformed = True
    if has_malformed:
        print("\nERROR: Malformed or duplicate markers detected.", file=sys.stderr)
        return 2
    if has_conflict:
        print("\nNotice: Conflicts detected. Approval required.", file=sys.stderr)
        return 1
    print("\nPreflight clean: no conflicts detected.")
    return 0


def run_apply(target_repo: Path, payloads: dict[str, bytes], approve_conflicts: bool) -> int:
    checks = inspect_destinations(target_repo, payloads)
    for c in checks:
        if c.status == "MALFORMED_MARKER":
            print(f"ERROR: Cannot apply due to malformed marker in {c.rel_path}: {c.message}", file=sys.stderr)
            return 2
        if c.status == "CONFLICT" and not approve_conflicts:
            print(f"ERROR: Conflict in {c.rel_path}: {c.message}. Use --approve-conflicts to apply.", file=sys.stderr)
            return 1

    applied = 0
    for c in checks:
        if c.status in ("CREATE", "APPEND") or (c.status == "CONFLICT" and approve_conflicts):
            if c.target_path and c.write_content is not None:
                c.target_path.parent.mkdir(parents=True, exist_ok=True)
                if isinstance(c.write_content, bytes):
                    c.target_path.write_bytes(c.write_content)
                else:
                    c.target_path.write_text(c.write_content, encoding="utf-8")
                print(f"Wrote {c.rel_path} ({c.status})")
                applied += 1
        elif c.status == "PRESERVE":
            print(f"Preserved {c.rel_path}")
        elif c.status == "NOOP":
            print(f"No-op (identical) {c.rel_path}")

    errs = verify_installed(target_repo, payloads)
    if errs:
        print("\nVerification failed after write:", file=sys.stderr)
        for err in errs:
            print(f"  - {err}", file=sys.stderr)
        return 1
    print(f"\nSuccess: {applied} destination(s) updated, all rule bytes and link targets verified.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="Preflight inspect destinations without writing")
    mode.add_argument("--apply", action="store_true", help="Apply approved rule bytes to target repository")
    parser.add_argument("target", type=Path, help="Target repository directory")
    parser.add_argument("--approve-conflicts", action="store_true", help="Approve overwriting conflicting sections")
    args = parser.parse_args(argv)

    target_repo = args.target.resolve()
    if not target_repo.is_dir():
        print(f"Error: Target directory does not exist: {target_repo}", file=sys.stderr)
        return 1

    payloads = load_payloads()
    if args.check:
        return run_check(target_repo, payloads)
    if args.apply:
        return run_apply(target_repo, payloads, args.approve_conflicts)
    return 0


if __name__ == "__main__":
    sys.exit(main())


