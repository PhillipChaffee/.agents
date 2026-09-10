#!/usr/bin/env bash
# Sync kit content from this repo (canonical) into a target location.
# Targets: agents (default, ~/.agents protocol layout) and cursor (~/.cursor
# kit layout). Non-destructive by default; manages only paths listed in its
# own stamp manifest.
set -euo pipefail

cd "$(dirname "$0")/.."
REPO_ROOT=$(pwd)
KIT_REPO="PhillipChaffee/.agents"
KIT_VERSION=$(git describe --tags --abbrev=0 2>/dev/null || git rev-parse --short HEAD 2>/dev/null || echo dev)

TARGET="agents"
ADOPT=0
FORCE=0
DRY_RUN=0
PRUNE=0
UNINSTALL=0
PULL=0

usage() {
  cat <<'USAGE'
Usage: scripts/install.sh [flags]

  --target agents   Install into ~/.agents (protocol layout, default)
  --target cursor   Install into ~/.cursor (Cursor kit layout)
  --adopt           One-time: bind an existing ~/.cursor kit to this repo
  --force           Overwrite unstamped files that differ
  --dry-run         Print actions without writing anything
  --prune           Also remove stamped files whose source disappeared
  --uninstall       Remove everything this script manages, then the stamp
  --pull            Reverse-sync kit-managed files from the target into the repo
  --help            This text

Safety: never touches mcp.json/models.json (repo templates) or any
un-managed file in the target home. The cursor target refuses to run
against a ~/.cursor that has no kit stamp unless --adopt is passed.
USAGE
}

while [ $# -gt 0 ]; do
  case "$1" in
    --target) TARGET="${2:?}"; shift 2 ;;
    --adopt) ADOPT=1; shift ;;
    --force) FORCE=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    --prune) PRUNE=1; shift ;;
    --uninstall) UNINSTALL=1; shift ;;
    --pull) PULL=1; shift ;;
    --help|-h) usage; exit 0 ;;
    *) echo "Unknown flag: $1" >&2; usage >&2; exit 2 ;;
  esac
done

case "$TARGET" in
  agents) STAMP_DIR="${HOME:?}/.agents" ;;
  cursor) STAMP_DIR="${HOME:?}/.cursor" ;;
  *) echo "Unknown target: $TARGET (agents|cursor)" >&2; exit 2 ;;
esac
STAMP_FILE="$STAMP_DIR/.kit-stamp"

# The adopt gate protects a pre-existing native ~/.cursor from being
# clobbered by a first run that has no record of what it owns.
if [ "$TARGET" = "cursor" ] && [ -d "$STAMP_DIR" ] && [ ! -f "$STAMP_FILE" ] && [ "$ADOPT" -eq 0 ]; then
  cat >&2 <<ERR
Refusing to install into $STAMP_DIR: it exists but has no kit stamp.
If this is your existing kit, re-run with --adopt to bind it to this repo
(one-time). The script only manages paths it records in its own stamp.
ERR
  exit 3
fi

# Build the source->dest mapping (tab-separated, relative paths).
# Field 3: copy | cursor-agent (frontmatter filtered to Cursor keys).
build_mapping() {
  local skill_dir id f rel
  for skill_dir in skills/*/; do
    id=$(basename "$skill_dir")
    if [ "$TARGET" = "agents" ]; then
      printf 'skills/%s/SKILL.md\tskills/%s/skill.md\tcopy\n' "$id" "$id"
    else
      printf 'skills/%s/SKILL.md\tskills/%s/SKILL.md\tcopy\n' "$id" "$id"
    fi
    while IFS= read -r f; do
      rel=${f#./}
      case "$rel" in
        skills/*/SKILL.md) continue ;;
      esac
      printf 'skills/%s/%s\tskills/%s/%s\tcopy\n' "$id" "$rel" "$id" "$rel"
    done < <(cd "$skill_dir" && find . -type f -name '*.md' ! -name 'SKILL.md' | sed 's|^\./||')
  done
  for f in agents/*/; do
    id=$(basename "$f")
    if [ "$TARGET" = "agents" ]; then
      printf 'agents/%s/agent.md\tagents/%s/agent.md\tcopy\n' "$id" "$id"
    else
      printf 'agents/%s/agent.md\tagents/%s.md\tcursor-agent\n' "$id" "$id"
    fi
  done
  for f in rules/*.md; do
    if [ "$TARGET" = "agents" ]; then
      printf '%s\t%s\tcopy\n' "$f" "$f"
    else
      printf '%s\t%s\tcopy\n' "$f" "${f%.md}.mdc"
    fi
  done
  if [ "$TARGET" = "agents" ] && [ -f agents.md ]; then
    printf 'agents.md\tagents.md\tcopy\n'
  fi
}

MAPPING=$(build_mapping)

stamp_paths() {
  [ -f "$STAMP_FILE" ] || return 0
  tail -n +3 "$STAMP_FILE"
}

is_stamped() {
  stamp_paths | grep -Fxq -- "$1"
}

# Cursor agents keep only the frontmatter keys Cursor understands;
# protocol keys (id/enabled/role/connection-type) would be noise there.
filter_cursor_agent() {
  python3 - "$1" "$2" <<'PY'
import sys

with open(sys.argv[1]) as f:
    text = f.read()
if not text.startswith("---\n"):
    sys.exit(0)
end = text.find("\n---", 4)
if end == -1:
    sys.exit(0)
fm, body = text[4:end], text[end + 4:]
keep = ("name:", "description:", "model:", "readonly:")
out = []
for line in fm.split("\n"):
    if line.split(":", 1)[0] + ":" in keep or (out and line[:1] in (" ", "\t") and line.strip()):
        out.append(line)
with open(sys.argv[2], "w") as f:
    if not body.startswith("\n"):
        body = "\n" + body
    f.write("---\n" + "\n".join(out) + "\n---" + body)
PY
}

copy_one() {
  # $1 src (repo-relative), $2 dest (target-relative), $3 mode
  local src="$1" dest="$2" mode="$3"
  local dest_abs="$STAMP_DIR/$dest" src_abs="$REPO_ROOT/$src"
  local action="" managed=0

  if [ ! -f "$src_abs" ]; then
    return 0
  fi
  if [ -f "$dest_abs" ]; then
    if is_stamped "$dest"; then
      action=UPDATE
      managed=1
    elif cmp -s "$src_abs" "$dest_abs"; then
      action=IDENTICAL
      managed=1
    elif [ "$FORCE" -eq 1 ]; then
      action=FORCE
      managed=1
    else
      echo "SKIP $dest (unstamped, differs — use --force to overwrite)"
      return 1
    fi
  else
    action=ADD
    managed=1
  fi

  if [ "$DRY_RUN" -eq 1 ]; then
    echo "$action $dest"
  else
    mkdir -p "$(dirname "$dest_abs")"
    if [ "$mode" = "cursor-agent" ]; then
      filter_cursor_agent "$src_abs" "$dest_abs"
    else
      cp "$src_abs" "$dest_abs"
    fi
    echo "$action $dest"
  fi
  return 0
}

new_manifest() {
  printf 'kit_version %s\nkit_repo %s\n' "$KIT_VERSION" "$KIT_REPO"
}

run_install() {
  local wrote=0 skipped=0 line src dest mode
  local MANIFEST_TMP
  MANIFEST_TMP=$(mktemp)
  new_manifest > "$MANIFEST_TMP"
  while IFS=$'\t' read -r src dest mode; do
    [ -n "$src" ] || continue
    if copy_one "$src" "$dest" "$mode"; then
      wrote=$((wrote + 1))
      printf '%s\n' "$dest" >> "$MANIFEST_TMP"
    else
      skipped=$((skipped + 1))
    fi
  done <<EOF
$MAPPING
EOF
  # Previously stamped paths that still exist stay managed even when
  # their source vanished from this run's mapping (prune handles removal).
  local p
  while IFS= read -r p; do
    [ -n "$p" ] || continue
    if grep -Fxq -- "$p" "$MANIFEST_TMP"; then
      continue
    fi
    if [ -f "$STAMP_DIR/$p" ]; then
      printf '%s\n' "$p" >> "$MANIFEST_TMP"
    fi
  done <<EOF
$(stamp_paths)
EOF
  if [ "$PRUNE" -eq 1 ]; then
    while IFS= read -r p; do
      [ -n "$p" ] || continue
      if grep -Fxq -- "$p" "$MANIFEST_TMP"; then
        continue
      fi
      if [ -f "$STAMP_DIR/$p" ]; then
        echo "PRUNE $p"
        [ "$DRY_RUN" -eq 1 ] || rm -f "$STAMP_DIR/$p"
      fi
    done <<EOF
$(stamp_paths)
EOF
  fi
  if [ "$DRY_RUN" -eq 0 ]; then
    mkdir -p "$STAMP_DIR"
    mv "$MANIFEST_TMP" "$STAMP_FILE"
  else
    rm -f "$MANIFEST_TMP"
  fi
  echo "mcp.json and models.json are repo templates; the installer never writes them."
  echo "done: target=$TARGET version=$KIT_VERSION wrote/updated=$wrote skipped=$skipped"
}

run_uninstall() {
  if [ ! -f "$STAMP_FILE" ]; then
    echo "no stamp at $STAMP_FILE — nothing installed to uninstall"
    return 0
  fi
  local removed=0 p
  while IFS= read -r p; do
    [ -n "$p" ] || continue
    if [ -f "$STAMP_DIR/$p" ]; then
      echo "REMOVE $p"
      [ "$DRY_RUN" -eq 1 ] || rm -f "$STAMP_DIR/$p"
      removed=$((removed + 1))
    fi
  done <<EOF
$(stamp_paths)
EOF
  if [ "$DRY_RUN" -eq 0 ]; then
    rm -f "$STAMP_FILE"
  fi
  echo "uninstalled: removed=$removed (stamp deleted; unmanaged files untouched)"
}

run_pull() {
  local changed=0 line src dest mode
  while IFS=$'\t' read -r src dest mode; do
    [ -n "$src" ] || continue
    if [ -f "$STAMP_DIR/$dest" ] && ! cmp -s "$STAMP_DIR/$dest" "$REPO_ROOT/$src"; then
      echo "PULL $dest -> $src"
      [ "$DRY_RUN" -eq 1 ] || cp "$STAMP_DIR/$dest" "$REPO_ROOT/$src"
      if [ "$mode" = "cursor-agent" ]; then
        echo "  note: $src pulled from Cursor layout — vendor key diffs may need manual reconcile"
      fi
      changed=$((changed + 1))
    fi
  done <<EOF
$MAPPING
EOF
  echo "pull complete: $changed file(s) changed in repo working tree (not committed)"
}

if [ "$UNINSTALL" -eq 1 ]; then
  run_uninstall
elif [ "$PULL" -eq 1 ]; then
  run_pull
else
  run_install
fi