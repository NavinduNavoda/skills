---
name: ask-rats
description: Say which rat skill to run next, based on the current plan's state.
disable-model-invocation: true
---

Shared scripts live in `../rat-kit/` next to this skill. Run `python3 <rat-kit>/scripts/rat.py status` from the user's folder, then answer with the one skill to run next and a one-line reason.

| State | Run |
|---|---|
| `plan: null` | `/start-rat <what to build>`. Needs a clean working folder. |
| `hint: review`, next commit `built` | Review the files in the working folder, edit anything, then `/next-rat`. |
| `hint: review-while-building` | Review now. `/next-rat` waits for the background build. |
| `questions` not empty | `/next-rat`. It settles the builder's questions first. |
| `hint: resume` | `/next-rat`. It rebuilds the next commit after a restart. |
| `hint: finish` | `/next-rat`. It cleans up the worktree. |
| `locked` set | Another session is running this plan. Finish there, or wait 30 minutes for the lock to expire. |

Also mention these when they fit what the user said:
- `/why-rat <WHY comment or file:line>` when a choice in the code is unclear.
- `/decide-rat` when the user stated a rule that should hold for the whole project.

Show the plan file path from `status` so the user can open it.
