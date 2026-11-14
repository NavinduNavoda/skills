#!/usr/bin/env bash
# Remove the links install-to-claude.sh made in ~/.claude.
# It removes only links that point into this repo or a .agents folder, and
# moves back the newest backup install made of a real file at that path.
set -euo pipefail
shopt -s nullglob

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
claude="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"

is_ours() {
  local target
  target="$(readlink "$1")"
  [[ "$target" == "$repo/"* || "$target" == *".agents/"* ]]
}

restore_backup() {
  local dest="$1" newest
  newest="$(compgen -G "$dest.bak.*" | sort | tail -1 || true)"
  [[ -n "$newest" ]] || return 0
  mv "$newest" "$dest"
  echo "restored $dest from $(basename "$newest")"
}

unlink_ours() {
  local dest="$1"
  [[ -L "$dest" ]] && is_ours "$dest" || return 0
  rm "$dest"
  echo "removed $dest"
  restore_backup "$dest"
}

unlink_ours "$claude/CLAUDE.md"

for l in "$claude"/skills/* "$claude"/agents/*; do
  unlink_ours "$l"
done
