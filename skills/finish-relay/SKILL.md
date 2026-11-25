---
name: finish-relay
description: Finish a relay plan in one shot. Commits the commit under review, brings in the built one from the background worktree, then builds and commits every remaining commit in the user's folder without stopping for review.
disable-model-invocation: true
---

Use this when the user trusts the rest of the plan and wants it done now. Every commit still lands on its own, with its own title, checks and WHY notes. Only the review pause between them goes away.

This skill uses the shared relay files in `../start-relay/` and the steps of `../next-relay/`, next to this skill's folder. If either folder is missing, tell the user to install the `start-relay` and `next-relay` skills too, and stop. Set `RELAY="python3 ../start-relay/scripts/relay.py"` with the full path. If a `RELAY` command fails, do that step by hand and tell the user.

1. **Take the lock.** `$RELAY lock`. If another session holds it, tell the user and stop. Then `$RELAY status`.
   - `plan: null`: tell the user there is no relay to finish, and stop.
   - `hint: finish`: go to step 8.
   - `hint: resume`: no commit is in review. Skip to step 6.

2. **Ask everything up front.** Read the plan and the titles of every commit not done yet. Settle each `questions-N.md` as `/next-relay` step 2 does, then delete it. List anything in the remaining commits that `../start-relay/RULES.md` says to ask about, like a new dependency, and ask it all in one round. Record the answers in the plan's Decisions section. After this round, don't stop to ask again unless step 6 hits a hard stop.

3. **Finalize the commit in review.** `$RELAY finalize`. Note `user_committed`, `changed` and `why_notes` for the summary.

4. **Bring in the background build.** Look at `next` in the finalize output.
   - No `next`: go to step 8.
   - `next` is `built`: bring it as `/next-relay` step 5 does, classifying with `../next-relay/CLASSIFY.md` when `changed` is true. NONE or SMALL: `$RELAY bring <N+1>` and patch it to fit. BIG: rebuild it in the user's folder per `../start-relay/BUILD.md`. Resolve `bring` conflicts yourself.
   - `next` is `building`: it counts as running only if you launched it in this conversation. If so, wait for it, then apply it by hand, since `finalize` wrote no patch: `git diff --binary refs/relay/<id>/base-<N> refs/relay/<id>/built-<N+1> -- . ':(exclude)docs/adr' | git apply --3way`, and treat it like `built`. Otherwise treat it as dead and build it in the user's folder per `../start-relay/BUILD.md`.
   - `next` is `planned`: build it in the user's folder per `../start-relay/BUILD.md`.

5. **Commit it.** Run the commands from `$RELAY checks` and fix failures. Then `$RELAY snapshot <N+1>` and `$RELAY finalize`. This strips its WHY lines into the plan and commits it with its title.

6. **Build the rest, one at a time.** For each remaining commit k, in order:
   - Build it in the user's folder per `../start-relay/BUILD.md`, from the plan and the code as it is now. Never launch a background build.
   - Run the checks and fix failures.
   - `$RELAY snapshot k`, then `$RELAY finalize`.
   - If a later commit no longer fits after what you built, update the plan with `$RELAY set-commits` and say so in the summary.

   **Hard stops.** Stop the loop, leave the current commit uncommitted and snapshotted, and tell the user to run `/next-relay` after they decide, when:
   - a commit conflicts with an ADR in `docs/adr/`,
   - a commit needs something `RULES.md` says to ask about that step 2 didn't cover,
   - checks still fail after a real attempt to fix them.

7. **Verify.** When no commits remain, run the checks once more on the final tree. Run `git log --oneline <plan base>..HEAD` and confirm one commit per plan entry, plus any `chore: remove WHY comments` commits.

8. **Finish.** `$RELAY finish`. It removes the worktree, the `relay/<id>` branch and the relay refs.

9. **Hand over.** Add a dated line to the plan's Session log: finished in one shot, which commits were built here, and decisions made in chat. Run `$RELAY unlock` if `finish` didn't run. Tell the user:
   - the commits made, one line each with the files they touch
   - each decision you made without asking, one line with its reason
   - anything rebuilt or re-planned, and why
   - how many WHY notes moved to the plan, and the plan file path
   - nothing was pushed
