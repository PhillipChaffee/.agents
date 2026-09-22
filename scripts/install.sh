#!/usr/bin/env bash
# Sync kit content from this repo (canonical) into ~/.agents (the .agents
# protocol layout). Non-destructive by default; manages only paths listed in
# its own stamp manifest.
set -euo pipefail

cd "$(dirname "$0")/.."
REPO_ROOT=$(pwd)
KIT_REPO="PhillipChaffee/.agents"
KIT_VERSION=$(git describe --tags --abbrev=0 2>/dev/null || git rev-parse --short HEAD 2>/dev/null || echo dev)

FORCE=0
DRY_RUN=0
PRUNE=0
UNINSTALL=0
PULL=0

usage() {
	cat <<'USAGE'
Usage: scripts/install.sh [flags]

  --target agents   Install into ~/.agents (protocol layout, default)
  --force           Overwrite unstamped files that differ
  --dry-run         Print actions without writing anything
  --prune           Also remove stamped files whose source disappeared
  --uninstall       Remove everything this script manages, then the stamp
  --pull            Reverse-sync kit-managed files from the target into the repo
  --help            This text

Safety: never touches any un-managed file in the target home. The kit pins no
models (docs/adr/0001): the installer asks for your fast/main/deep choices and
writes a consumer-local models.json beside the installed kit.
USAGE
}

while [ $# -gt 0 ]; do
	case "$1" in
	--target)
		TARGET="${2:?}"
		shift 2
		;;
	--force)
		FORCE=1
		shift
		;;
	--dry-run)
		DRY_RUN=1
		shift
		;;
	--prune)
		PRUNE=1
		shift
		;;
	--uninstall)
		UNINSTALL=1
		shift
		;;
	--pull)
		PULL=1
		shift
		;;
	--help | -h)
		usage
		exit 0
		;;
	*)
		echo "Unknown flag: $1" >&2
		usage >&2
		exit 2
		;;
	esac
done

TARGET="${TARGET:-agents}"
if [ "$TARGET" != "agents" ]; then
	echo "Unknown target: $TARGET (only 'agents' is supported)" >&2
	exit 2
fi
STAMP_DIR="${HOME:?}/.agents"
STAMP_FILE="$STAMP_DIR/.kit-stamp"

# Build the source->dest mapping (tab-separated, relative paths).
build_mapping() {
	local skill_dir id f rel
	for skill_dir in skills/*/; do
		id=$(basename "$skill_dir")
		printf 'skills/%s/SKILL.md\tskills/%s/skill.md\n' "$id" "$id"
		while IFS= read -r f; do
			rel=${f#./}
			case "$rel" in
			skills/*/SKILL.md) continue ;;
			esac
			printf 'skills/%s/%s\tskills/%s/%s\n' "$id" "$rel" "$id" "$rel"
		done < <(cd "$skill_dir" && find . -type f -name '*.md' ! -name 'SKILL.md' | sed 's|^\./||')
	done
	for f in agents/*/; do
		id=$(basename "$f")
		printf 'agents/%s/agent.md\tagents/%s/agent.md\n' "$id" "$id"
	done
	for f in rules/*.md; do
		printf '%s\t%s\n' "$f" "$f"
	done
	# The distilled instruction layer installs at the protocol home root,
	# where consumers' harnesses auto-load it; the stamp system owns any
	# collision with a pre-existing unstamped ~/.agents/agents.md (SKIP
	# unless byte-identical or --force).
	printf 'agents.kit.md\tagents.md\n'
}

MAPPING=$(build_mapping)

stamp_paths() {
	[ -f "$STAMP_FILE" ] || return 0
	# Only accept sane relative paths; a corrupted or tampered stamp must
	# never make rm/cp resolve outside the target root.
	tail -n +3 "$STAMP_FILE" | grep -E '^[A-Za-z0-9._/-]+$' | grep -v '\.\.' || true
}

is_stamped() {
	stamp_paths | grep -Fxq -- "$1"
}

# Consumer-local models config: the installer asks once and writes the
# answers beside the installed kit. Never written into the repo; never
# carries anything but the consumer's own tier choices.
write_models_config() {
	local file="$STAMP_DIR/models.json"
	if [ ! -t 0 ]; then
		echo "models: not interactive — skipping tier prompt (configure your harness manually)"
		return 0
	fi
	echo "Choose your harness's model for each tier (the kit pins none — ADR-0001)."
	read -rp "fast subagent model: " fast
	read -rp "main subagent model: " main
	read -rp "deep model (optional, blank = same as main): " deep
	deep=${deep:-$main}
	[ "$DRY_RUN" -eq 1 ] && {
		echo "DRY-RUN would write $file"
		return 0
	}
	cat >"$file" <<JSON
{
  "_note": "Consumer-local model choices. Configure your harness to use these tiers; never commit provider keys or tokens.",
  "presets": {
    "fast": "$fast",
    "main": "$main",
    "deep": "$deep"
  }
}
JSON
	echo "wrote $file"
}

copy_one() {
	# $1 src (repo-relative), $2 dest (target-relative)
	# Returns: 0 written/managed, 1 skipped, 2 no source
	local src="$1" dest="$2"
	local dest_abs="$STAMP_DIR/$dest" src_abs="$REPO_ROOT/$src"
	local action=""

	if [ ! -f "$src_abs" ]; then
		return 2
	fi
	if [ -f "$dest_abs" ]; then
		if is_stamped "$dest"; then
			action=UPDATE
		elif cmp -s "$src_abs" "$dest_abs"; then
			# Unstamped but byte-identical to the source: adopt it as managed so
			# future updates and --prune own it.
			action=IDENTICAL
		elif [ "$FORCE" -eq 1 ]; then
			action=FORCE
		else
			echo "SKIP $dest (unstamped, differs — use --force to overwrite)"
			return 1
		fi
	else
		action=ADD
	fi

	if [ "$DRY_RUN" -eq 1 ]; then
		echo "$action $dest"
	else
		mkdir -p "$(dirname "$dest_abs")"
		cp "$src_abs" "$dest_abs"
		echo "$action $dest"
	fi
	return 0
}

new_manifest() {
	printf 'kit_version %s\nkit_repo %s\n' "$KIT_VERSION" "$KIT_REPO"
}

run_install() {
	local wrote=0 skipped=0 src dest
	local MANIFEST_TMP
	write_models_config
	MANIFEST_TMP=$(mktemp)
	new_manifest >"$MANIFEST_TMP"
	while IFS=$'\t' read -r src dest; do
		[ -n "$src" ] || continue
		local rc=0
		copy_one "$src" "$dest" || rc=$?
		case $rc in
		0)
			wrote=$((wrote + 1))
			printf '%s\n' "$dest" >>"$MANIFEST_TMP"
			;;
		1) skipped=$((skipped + 1)) ;;
		2) : ;;
		esac
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
			printf '%s\n' "$p" >>"$MANIFEST_TMP"
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
	cat <<GUIDE
MCP setup (configure in your harness's own config; the kit never writes MCP files):
  GitHub   https://github.com/github/github-mcp-server
  GitLab   https://docs.gitlab.com/ee/user/gitlab_duo/mcp/
  Linear   https://mcp.linear.app/sse
Models: the kit pins none; configure your harness's subagent model (see rules/subagents.md).
done: target=agents version=$KIT_VERSION wrote/updated=$wrote skipped=$skipped
GUIDE
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
	local changed=0 src dest
	while IFS=$'\t' read -r src dest; do
		[ -n "$src" ] || continue
		if [ -f "$STAMP_DIR/$dest" ] && ! cmp -s "$STAMP_DIR/$dest" "$REPO_ROOT/$src"; then
			echo "PULL $dest -> $src"
			[ "$DRY_RUN" -eq 1 ] || cp "$STAMP_DIR/$dest" "$REPO_ROOT/$src"
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
