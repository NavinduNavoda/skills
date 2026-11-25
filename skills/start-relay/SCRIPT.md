# The relay script

The relay skills build a feature as small commits. The user reviews commit N in their folder while a background agent builds N+1 in a separate worktree. `start-relay` holds the files every relay skill shares. `next-relay`, `finish-relay`, `why-relay` and `status-relay` reach them at `../start-relay/`.

## Files

- [scripts/relay.py](scripts/relay.py): state, snapshots, WHY stripping, change detection. Tests: `python3 -m unittest test_relay.py` from `scripts/`.
- [BUILD.md](BUILD.md): how to build one commit. Every builder follows it.
- [BACKGROUND.md](BACKGROUND.md): how to launch a background build. The only agent-specific part.
- [RULES.md](RULES.md): when to decide and when to ask. Every relay step follows it.

## What the script does

- Uses the Python standard library only. Nothing to install.
- Makes no network calls.
- Runs only `git`, with argument lists and no shell.
- Keeps its own data inside the repo's git folder (see Storage), so none of it is committed.
- Changes the user's folder in two commands only. `finalize` removes `WHY:` lines from the changed files and commits everything in the folder (`git add -A`) on the current branch. `bring` applies the next commit's patch, uncommitted.
- `init` refuses a dirty working tree. `finish` deletes only the plan's own worktree, its `relay/<id>` branch, its `refs/relay/<id>/` refs and its `.diff` files.

## Running the script

`RELAY="python3 <start-relay>/scripts/relay.py"`. Every command prints JSON. When a command prints `{"error": ...}` or fails, do that step by hand and tell the user which step fell back and why.

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
agent-worktrees/000-auth/      background build copy, branch relay/000-auth, never pushed
```
