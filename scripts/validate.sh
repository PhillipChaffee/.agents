#!/usr/bin/env bash
# Validate kit structure: frontmatter contracts, cross-reference resolution,
# stale-path detection, and install-script sanity. Exit 1 on any FAIL.
set -euo pipefail
cd "$(dirname "$0")/.."

if command -v python3 >/dev/null 2>&1; then
  python3 - <<'PY'
import re
import sys
from pathlib import Path

fails = []
warns = []


def fail(msg):
    fails.append(msg)


def warn(msg):
    warns.append(msg)


def split_fm(text, rel):
    if not text.startswith("---\n"):
        return None, None
    end = text.find("\n---", 4)
    if end == -1:
        return None, None
    return text[4:end], text[end + 4:]


def top_keys(fm):
    keys = {}
    order = []
    cur = None
    for line in fm.split("\n"):
        m = re.match(r"^([A-Za-z][A-Za-z0-9-]*):", line)
        if m:
            cur = m.group(1)
            keys[cur] = line
            order.append(cur)
    return keys, order


skills = sorted(d for d in Path("skills").iterdir() if (d / "SKILL.md").exists()) if Path("skills").is_dir() else []
skill_ids = {d.name for d in skills}
agents_dir = Path("agents")
agents = sorted(d for d in agents_dir.iterdir() if (d / "agent.md").exists()) if agents_dir.is_dir() else []
agent_ids = {d.name for d in agents}
rules_dir = Path("rules")
rule_ids = {p.stem for p in rules_dir.glob("*.md")} if rules_dir.is_dir() else set()

# 1. Skill frontmatter contract
for d in skills:
    rel = f"skills/{d.name}/SKILL.md"
    fm, _ = split_fm(d.joinpath("SKILL.md").read_text(), rel)
    if fm is None:
        fail(f"{rel}: missing or malformed frontmatter")
        continue
    keys, order = top_keys(fm)
    for k in ("description", "enabled", "id", "name"):
        if k not in keys:
            fail(f"{rel}: missing frontmatter key '{k}'")
    if keys.get("id", "").split("id:", 1)[-1].strip() != d.name:
        fail(f"{rel}: id does not match directory name")
    if order != sorted(order):
        warn(f"{rel}: frontmatter keys not sorted")

# 2. Agent frontmatter contract
for d in agents:
    rel = f"agents/{d.name}/agent.md"
    fm, _ = split_fm(d.joinpath("agent.md").read_text(), rel)
    if fm is None:
        fail(f"{rel}: missing or malformed frontmatter")
        continue
    keys, order = top_keys(fm)
    for k in ("connection-type", "description", "enabled", "id", "model", "name", "role"):
        if k not in keys:
            fail(f"{rel}: missing frontmatter key '{k}'")
    if keys.get("id", "").split("id:", 1)[-1].strip() != d.name:
        fail(f"{rel}: id does not match directory name")
    if order != sorted(order):
        warn(f"{rel}: frontmatter keys not sorted")

if not agents:
    warn("agents/ tree absent — agent-reference checks skipped")

AGENT_REF = re.compile(
    r"\b((?:cr|pr)-[a-z][a-z-]*|researcher-(?:lite|mid|deep)|"
    r"research-(?:planner|synthesizer)|refactor-(?:code|placement)-scout)\b"
)
SKILL_CMD = re.compile(r"`/([a-z][a-z0-9-]*)`")
SLASH_REF = re.compile(r"(?<![`\w:./>-])/([a-z][a-z0-9-]+)")
SKILL_PATH = re.compile(r"skills/([a-z][a-z0-9-]*)/SKILL\.md")
RULE_REF = re.compile(r"rules/([a-z][a-z0-9-]*)\.md")
EXTERNAL = {"autopilot", "create-skill", "create-rule", "canvas"}

md_files = sorted(Path("skills").rglob("*.md")) if Path("skills").is_dir() else []
for md in md_files:
    text = md.read_text()
    rel = str(md)
    # 3. Agent references resolve
    for ref in set(AGENT_REF.findall(text)):
        if agents and ref not in agent_ids:
            fail(f"{rel}: references unknown agent '{ref}'")
    # 4. Skill references resolve
    for ref in set(SKILL_CMD.findall(text)):
        if ref in EXTERNAL:
            continue
        if skill_ids and ref not in skill_ids:
            fail(f"{rel}: references unknown skill '/{ref}'")
    for ref in set(SLASH_REF.findall(text)):
        if ref in EXTERNAL:
            continue
        if skill_ids and ref not in skill_ids:
            fail(f"{rel}: references unknown skill '/{ref}'")
    for ref in set(SKILL_PATH.findall(text)):
        if skill_ids and ref not in skill_ids:
            fail(f"{rel}: references unknown skill path 'skills/{ref}/SKILL.md'")
    # 5. Rule references resolve; no stale Cursor-era paths in skills
    for ref in set(RULE_REF.findall(text)):
        if rules_dir.is_dir() and ref not in rule_ids:
            fail(f"{rel}: references unknown rule 'rules/{ref}.md'")
    # ~/.cursor/<x> mentions document an installed-kit location and are
    # legitimate; repo-relative .cursor/ paths are stale migration leftovers.
    if re.search(r"(?<!~/)\.cursor/(?:rules|skills|agents|plans)", text) or "RULE.mdc" in text:
        fail(f"{rel}: stale Cursor-era rule path")

for w in warns:
    print(f"WARN {w}")
for f in fails:
    print(f"FAIL {f}")
print(f"checked {len(skills)} skills, {len(agents)} agents, {len(rule_ids)} rules, {len(md_files)} skill markdown files")
sys.exit(1 if fails else 0)
PY
else
  echo "FAIL python3 is required for validation" >&2
  exit 1
fi

# 6. Install script sanity (when present)
if [ -f scripts/install.sh ]; then
  bash -n scripts/install.sh || { echo "FAIL scripts/install.sh: syntax error"; exit 1; }
  echo "PASS scripts/install.sh syntax"
fi

echo "OK validation passed"