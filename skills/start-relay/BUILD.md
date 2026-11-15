# Building one commit

You build commit N of a relay plan in a given folder: the user's folder, or the agent worktree for a background build.

1. **Read first.** Read the plan file: Goal, Commits, Decisions, Open questions. Read every ADR in the user's `docs/adr/`, not the worktree's copy, which may be older. Follow the ADRs. If commit N conflicts with one, stop and report the conflict. Read the repo's `CODING_STANDARDS.md` if it has one. Then read these if they are installed next to `start-relay`: `../nv-coding-style/SKILL.md`, `../nv-coding-style/STANDARDS.md` and `../nv-testing/SKILL.md`. Follow them. The repo's file wins where they disagree. Without any of them, match the code around you.
2. **Stay in scope.** Build only what commit N's title and the plan say. The commit must compile and pass the checks from `relay.py checks` on its own. Aim for a diff a person reviews in a few minutes.
   Add tests only for code on the "Test" list of `nv-testing`, or where the repo's own rules ask for them. A commit with nothing on that list adds no tests.
3. **WHY comments.** Add one only for a choice that needed judgment: a data structure, a library, an error-handling strategy, a tradeoff. Never for routine code. Put it on its own line directly above the code, in the file's comment syntax, and name the alternative:
   `// WHY: Map over array because lookups by id happen on every render`
   Keep it to one line. Files without comments, like JSON, get no WHY line.
   Write no other comments. Follow the Comments section of `nv-coding-style`.
   Record each judgment call as a decision too. In the user's folder, add it to the plan's Decisions section. In a background build, append `Decision: <choice and reason>` to `<state folder>/questions-N.md`, since you may not edit the plan.
4. **Dependencies.** Don't install packages or edit lock files. If commit N needs a new dependency, write it as a question.
5. **Questions.** Pick the sensible default and build with it. Record it as a `Decision:` line. Write a `Q:` entry only for something `RULES.md` says to ask about, such as a dependency not approved in the plan:
   ```
   Q: <question>
   Default used: <what you did>
   Where: <file:line>
   ```
6. **Check.** Run the commands from `relay.py checks` in the folder you built in and fix failures before you finish.
7. **Format.** Run the repo's formatter after building, so the commit stays formatted when its `WHY:` lines are stripped.

## Background builds only

- Work only inside the worktree path you were given. Never edit the user's folder, never push, never switch branches.
- Finish with `python3 <start-relay>/scripts/relay.py --plan <id> wt-commit N`, run from inside the worktree.
- Report in two lines: what you built, and how many questions you wrote.
