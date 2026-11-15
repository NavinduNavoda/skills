---
name: start-relay
description: Start a feature as small commits. The user reviews each commit while the agent builds the next one in the background.
disable-model-invocation: true
argument-hint: "What do you want to build?"
---

This folder holds the files every relay skill shares. `SCRIPT.md` describes them. Set `RELAY="python3 <this folder>/scripts/relay.py"`. If a `RELAY` command fails, do that step by hand and tell the user.

1. **Check the branch.** Run `$RELAY status`. If this branch already has a plan, tell the user to run `/next-relay` and stop. If on the default branch, create `feat/<slug>` first.

2. **Decide, don't ask.** Read enough of the code to plan and decide the open choices yourself. Ask only what the Decisions section of `RULES.md` lists, in one round.

3. **Create the plan.** `$RELAY init <slug> "<title>"`. If it refuses a dirty tree, ask the user to commit or stash, and stop.

4. **Write the plan.** Split the feature into small commits. Each one compiles, passes checks, and reviews in a few minutes. Fill the plan file's Goal and Decisions sections, including the user's answers. Then `$RELAY set-commits "feat: ..." "feat: ..."` with Conventional Commit titles.

5. **Build commit 1** in the user's folder, following `BUILD.md`. Leave it uncommitted. Run `$RELAY snapshot 1`.

6. **Start commit 2** in the background: `$RELAY building 2`, then launch it as `BACKGROUND.md` says. Never start more than one commit ahead.

7. **Hand over.** Add a dated line to the plan's Session log. Tell the user:
   - what commit 1 does and which files it touches
   - each decision you made, one line with its reason
   - that `WHY:` comments explain judgment calls and disappear when the commit is finalized
   - they can edit anything, then run `/next-relay`
   - the plan file path
