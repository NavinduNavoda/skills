#!/usr/bin/env bash
# Symlink AGENTS.md, skills and agents from this repo into ~/.claude.
# Safe to re-run: existing links are replaced, real files are backed up first.
set -euo pipefail
shopt -s nullglob

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
claude="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"

link() {
  local src="$1" dest="$2"
  if [[ -e "$dest" && ! -L "$dest" ]]; then
    mv "$dest" "$dest.bak.$(date +%s)"
    echo "backed up $dest"
  fi
  ln -sfn "$src" "$dest"
  echo "linked $dest"
}

prune() {
  local dir="$1"
  for l in "$dir"/*; do
    [[ -L "$l" && ! -e "$l" ]] || continue
    [[ "$(readlink "$l")" == "$repo/"* || "$(readlink "$l")" == *".agents/"* ]] || continue
    rm "$l"
    echo "removed stale $l"
  done
}

mkdir -p "$claude/skills" "$claude/agents"

link "$repo/AGENTS.md" "$claude/CLAUDE.md"

for d in "$repo"/skills/*/; do
  link "${d%/}" "$claude/skills/$(basename "$d")"
done

for f in "$repo"/agents/*.md; do
  link "$f" "$claude/agents/$(basename "$f")"
done

prune "$claude/skills"
prune "$claude/agents"
