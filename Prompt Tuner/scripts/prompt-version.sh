#!/usr/bin/env bash
#
# prompt-version.sh — lightweight prompt version history for the Prompt Tuner repo.
#
# Snapshots an agent's prompt files into versions/<Agent>/<stamp>__<label>/ so you can
# roll back to a known-good version WITHOUT relying on git commits/pushes. Pairs with
# git tags (see `tag` below and the /prompt-version skill) for durable, shareable markers.
#
# Usage:
#   scripts/prompt-version.sh save    <agent> <label> [note...]   # snapshot current prompts
#   scripts/prompt-version.sh list    [agent]                     # list snapshots
#   scripts/prompt-version.sh diff    <agent> <label> [file]      # current vs a snapshot
#   scripts/prompt-version.sh restore <agent> <label>            # roll back to a snapshot
#   scripts/prompt-version.sh tag     <agent> <label> [note...]   # git tag the current HEAD
#
#   <agent> = any bot folder (a top-level dir with CHANGELOG.md + a prompt), case-insensitive
#   <label> is a short kebab slug, e.g. stable-2026-07-15 or pre-inbound-build.
#
# Notes:
# - A snapshot copies every *.md in the agent's dir EXCEPT CHANGELOG.md (history, never restored).
# - `restore` auto-snapshots the current state first (label: pre-restore-<stamp>) so it is reversible.
# - Snapshots live under versions/ which is git-ignored by default (local safety net).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSIONS_DIR="$REPO_ROOT/versions"

die() { echo "error: $*" >&2; exit 1; }

# Discover bot folders instead of hard-coding them (2026-08-05). The repo now serves multiple
# projects (Blue Dots: KKB/DKB/Maya; Purple Dots: ...), so a new bot must NOT require editing this
# script — a hard-coded case list meant `save` died on any newly registered bot, which silently
# blocked the "snapshot before edit" law for exactly the bots most likely to need it.
# A bot folder = a top-level dir holding a CHANGELOG.md and at least one other *.md prompt file.
bot_dirs() {
  local d
  for d in "$REPO_ROOT"/*/; do
    d="${d%/}"
    [ -f "$d/CHANGELOG.md" ] || continue
    # must have at least one prompt file besides CHANGELOG.md
    if [ -n "$(find "$d" -maxdepth 1 -type f -name '*.md' ! -name 'CHANGELOG.md' -print -quit)" ]; then
      basename "$d"
    fi
  done
}

resolve_agent() {
  local want known
  # normalise: lowercase, and treat - and _ as spaces so "purple-dots" matches "Purple Dots"
  want="$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]' | tr '_-' '  ')"
  while IFS= read -r known; do
    [ -n "$known" ] || continue
    if [ "$(printf '%s' "$known" | tr '[:upper:]' '[:lower:]' | tr '_-' '  ')" = "$want" ]; then
      echo "$known"; return 0
    fi
  done <<< "$(bot_dirs)"
  die "unknown agent '$1' (known bots: $(bot_dirs | paste -sd' ' -))"
}

stamp_now() { date +%Y-%m-%d_%H%M%S; }

snapshot_files() {  # $1 = agent dir path; prints matching files
  find "$1" -maxdepth 1 -type f -name '*.md' ! -name 'CHANGELOG.md' | sort
}

cmd_save() {
  [ $# -ge 2 ] || die "usage: save <agent> <label> [note...]"
  local agent label note src dest stamp
  agent="$(resolve_agent "$1")"; label="$2"; shift 2; note="${*:-}"
  src="$REPO_ROOT/$agent"
  [ -d "$src" ] || die "no such agent dir: $src"
  stamp="$(stamp_now)"
  dest="$VERSIONS_DIR/$agent/${stamp}__${label}"
  mkdir -p "$dest"
  local n=0
  while IFS= read -r f; do
    cp "$f" "$dest/"; n=$((n+1))
  done < <(snapshot_files "$src")
  [ "$n" -gt 0 ] || die "no prompt files found in $src"
  # per-agent history log
  local hist="$VERSIONS_DIR/$agent/HISTORY.md"
  [ -f "$hist" ] || printf '# %s — snapshot history\n\n' "$agent" > "$hist"
  printf -- '- **%s** — `%s` — %s _(%s files)_\n' "$stamp" "$label" "${note:-—}" "$n" >> "$hist"
  echo "saved: versions/$agent/${stamp}__${label}  ($n files)"
}

cmd_list() {
  local agents=()
  if [ $# -ge 1 ]; then
    agents=("$(resolve_agent "$1")")
  else
    while IFS= read -r a; do [ -n "$a" ] && agents+=("$a"); done <<< "$(bot_dirs)"
  fi
  for a in "${agents[@]}"; do
    echo "== $a =="
    if [ -d "$VERSIONS_DIR/$a" ]; then
      find "$VERSIONS_DIR/$a" -maxdepth 1 -type d -name '*__*' | sort | sed "s#$VERSIONS_DIR/$a/#  #"
    else
      echo "  (no snapshots)"
    fi
  done
}

find_snapshot() {  # $1 agent, $2 label -> prints dir path (matches suffix __<label>)
  local agent="$1" label="$2" hit
  hit="$(find "$VERSIONS_DIR/$agent" -maxdepth 1 -type d -name "*__${label}" 2>/dev/null | sort | tail -1)"
  [ -n "$hit" ] || die "no snapshot for $agent with label '$label' (try: list $agent)"
  echo "$hit"
}

cmd_diff() {
  [ $# -ge 2 ] || die "usage: diff <agent> <label> [file]"
  local agent snap
  agent="$(resolve_agent "$1")"; snap="$(find_snapshot "$agent" "$2")"
  if [ $# -ge 3 ]; then
    diff -u "$snap/$3" "$REPO_ROOT/$agent/$3" || true
  else
    local f base
    for f in "$snap"/*.md; do
      base="$(basename "$f")"
      echo "### $base"
      diff -u "$f" "$REPO_ROOT/$agent/$base" || true
    done
  fi
}

cmd_restore() {
  [ $# -eq 2 ] || die "usage: restore <agent> <label>"
  local agent snap f base
  agent="$(resolve_agent "$1")"; snap="$(find_snapshot "$agent" "$2")"
  # make the restore reversible: snapshot current first
  cmd_save "$agent" "pre-restore-$(stamp_now)" "auto-saved before restoring '$2'" >/dev/null
  for f in "$snap"/*.md; do
    base="$(basename "$f")"
    cp "$f" "$REPO_ROOT/$agent/$base"
    echo "restored: $agent/$base"
  done
  echo "done. (current state was auto-snapshotted first; restore is reversible.)"
}

cmd_tag() {
  [ $# -ge 2 ] || die "usage: tag <agent> <label> [note...]"
  local agent label note tagname
  agent="$(resolve_agent "$1")"; label="$2"; shift 2; note="${*:-stable marker}"
  tagname="$(printf '%s' "$agent" | tr '[:upper:]' '[:lower:]')-${label}"  # bash 3.2 (macOS) has no ${x,,}
  git -C "$REPO_ROOT" rev-parse --git-dir >/dev/null 2>&1 || die "not a git repo"
  if ! git -C "$REPO_ROOT" diff --quiet || ! git -C "$REPO_ROOT" diff --cached --quiet; then
    echo "note: working tree has uncommitted changes — this tag marks the last COMMIT, not the current files." >&2
    echo "      (the file snapshot from 'save' captures the current uncommitted state.)" >&2
  fi
  git -C "$REPO_ROOT" tag -a "$tagname" -m "$note"
  echo "tagged: $tagname -> $(git -C "$REPO_ROOT" rev-parse --short HEAD)"
}

sub="${1:-}"; shift || true
case "$sub" in
  save)    cmd_save "$@" ;;
  list)    cmd_list "$@" ;;
  diff)    cmd_diff "$@" ;;
  restore) cmd_restore "$@" ;;
  tag)     cmd_tag "$@" ;;
  *) sed -n '3,40p' "$0"; exit 1 ;;
esac
