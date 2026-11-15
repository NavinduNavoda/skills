---
name: status-relay
description: Say which relay skill to run next, based on the current plan's state.
disable-model-invocation: true
---

This skill uses the shared relay files in `../start-relay/`, next to this skill's folder. If that folder is missing, tell the user to install the `start-relay` skill too, and stop. Run `python3 ../start-relay/scripts/relay.py status` from the user's folder, then answer with the one skill to run next and a one-line reason.

| State | Run |
|---|---|
| `plan: null` | `/start-relay <what to build>`. Needs a clean working folder. |
| `hint: review`, next commit `built` | Review the files in the working folder, edit anything, then `/next-relay`. |
| `hint: review-while-building` | Review now. `/next-relay` waits for the background build. |
| `questions` not empty | `/next-relay`. It settles the builder's questions first. |
| `hint: resume` | `/next-relay`. It rebuilds the next commit after a restart. |
| `hint: finish` | `/next-relay`. It cleans up the worktree. |
| `locked` set | Another session is running this plan. Finish there, or wait 30 minutes for the lock to expire. |

Also mention these when they fit what the user said:
- `/why-relay <WHY comment or file:line>` when a choice in the code is unclear.
- `/nv-adr` when the user stated a rule that should hold for the whole project.

Show the plan file path from `status` so the user can open it.
