---
name: next-relay
description: Finalize the commit under review and bring in the next one, adapted to the user's edits.
disable-model-invocation: true
---

This skill uses the shared relay files in `../start-relay/`, next to this skill's folder. If that folder is missing, tell the user to install the `start-relay` skill too, and stop. Set `RELAY="python3 ../start-relay/scripts/relay.py"` with the full path. If a `RELAY` command fails, do that step by hand and tell the user.

1. **Take the lock.** `$RELAY lock`. If another session holds it, tell the user and stop. Then `$RELAY status`.
   - `hint: resume` (the session restarted after a finalize): build the first unfinished commit in the user's folder per `../start-relay/BUILD.md`, `$RELAY snapshot <n>`, go to step 7.
   - `hint: finish`: go to step 8.

2. **Settle the builder's questions.** For each `questions-N.md` in `status`, accept the builder's default unless it conflicts with the user's edits or the plan, and pick better yourself where it does. Ask only for a `Q:` that needs approval under `../start-relay/RULES.md`. Record every answer and `Decision:` line in the plan's Decisions section, then delete the file. List your choices in the hand-over.

3. **Wait for N+1.** If it shows `building`, wait for it to finish and tell the user you're waiting. A build counts as running only if you launched it in this conversation. Otherwise launch it again per `../start-relay/BACKGROUND.md`.

4. **Finalize N.** `$RELAY finalize`. It strips WHY lines into the plan, commits N, and writes the patch for N+1. Tell the user:
   - if `user_committed`, that you found their own commit and added `chore: remove WHY comments`
   - how many WHY notes moved to the plan

5. **Bring in N+1.**
   - No `next`: go to step 8.
   - `changed: false` and no differing answers: `$RELAY bring <N+1>`.
   - Otherwise classify per `CLASSIFY.md` in this skill's folder.
     - NONE: `$RELAY bring <N+1>`.
     - SMALL: `$RELAY bring <N+1>`, then fix it in the user's folder to fit their edits. List what you patched, so they review it with the rest.
     - BIG: don't bring it. Rebuild N+1 in the user's folder per `../start-relay/BUILD.md`, starting from their version. Tell the user it was rebuilt and why.
   - If `bring` reports conflicts, resolve the markers yourself and treat it as SMALL.
   - If anything changed, run the commands from `$RELAY checks`. On failure, fix it, or rebuild if the fix is big.

6. **Record N+1.** `$RELAY snapshot <N+1>`. If a rebuild changed the later plan, update it with `$RELAY set-commits`.

7. **Start N+2** if it exists: `$RELAY building <N+2>`, then launch it per `../start-relay/BACKGROUND.md`. Never more than one ahead.

8. **Finish** when no commits remain: `$RELAY finish`. Summarize the commits and point to the plan file.

9. **Hand over.** Add a dated line to the plan's Session log covering decisions made in chat. Run `$RELAY unlock`. Tell the user what is in review now and which files it touches.
