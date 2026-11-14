---
name: rat-kit
description: Shared scripts and rules used by start-rat, next-rat, why-rat, decide-rat and ask-rats. Not run on its own.
disable-model-invocation: true
user-invocable: false
---

The rat skills build a feature as small commits. The user reviews commit N in their folder while a background agent builds N+1 in a separate worktree.

## Files

- [scripts/rat.py](scripts/rat.py): state, snapshots, WHY stripping, change detection. Python standard library and git only. Tests: `python3 -m unittest test_rat.py` from `scripts/`.
- [BUILD.md](BUILD.md): how to build one commit. Every builder follows it.
- [BACKGROUND.md](BACKGROUND.md): how to launch a background build. The only agent-specific part.
- [CLASSIFY.md](CLASSIFY.md): the prompt for judging a user's edits as NONE, SMALL or BIG.

## Running the script

`RAT="python3 <this folder>/scripts/rat.py"`. Every command prints JSON. When a command prints `{"error": ...}` or fails, do that step by hand and tell the user which step fell back and why.

| Command | Does |
|---|---|
| `init <slug> "<title>"` | Refuses a dirty tree. Creates the plan file, state and worktree |
| `set-commits "<title>" ...` | Replaces the titles of commits not started yet |
| `snapshot N` | Records the user's folder as commit N in review, resets the worktree to it without WHY lines |
| `building N` / `wt-commit N` | Marks N as building / commits the worktree as N |
| `finalize` | Strips WHY lines into the plan, detects user changes, commits N, writes the patch for N+1 |
| `bring N` | Applies the patch for N to the user's folder, uncommitted |
| `checks` | Lists the type check and test commands it found |
| `status`, `lock`, `unlock`, `finish` | Read state, guard against two sessions, clean up at the end |

Pass `--plan <id>` before the command when running outside the user's branch, as in the worktree.

## Storage

All under the repo's git folder (`git rev-parse --git-common-dir`), so it is never committed and every worktree of the repo sees it:

```
agent-plans/000-auth.md        plan, decisions, WHY notes, session log
agent-state/000-auth/          state.json, lock, diffs, questions-N.md
agent-worktrees/000-auth/      background build copy, branch rat/000-auth, never pushed
```
