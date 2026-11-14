---
name: why-rat
description: Explain a decision in the current rat plan in depth, for a junior developer who wants to learn.
disable-model-invocation: true
argument-hint: "Which decision? A WHY comment, a file:line, or a question"
---

The user is a junior developer and wants to learn, not only to hear the answer. Shared scripts live in `../rat-kit/` next to this skill.

1. **Find the decision.** It may be a `WHY:` comment in the code, a line in the plan's WHY notes or Decisions (path from `python3 <rat-kit>/scripts/rat.py status`), or a question about the code. If it's unclear which one, ask.

2. **Explain it** in this order:
   - **What was chosen**, quoting the relevant code.
   - **The alternatives**: at least two, each with a short code sketch where it helps.
   - **The tradeoffs**: what each option costs and gains here, in this codebase. Use numbers where you can, like lookups per render or lines of code.
   - **The concepts**: name the patterns, data structures or architecture ideas involved, such as "dependency injection" or "hash map, O(1) lookup", and say in one line what each means.
   - **When the answer flips**: the situation where you'd pick an alternative.

3. **Check understanding.** End with one short question the user can answer to test themselves. Don't quiz further unless they want it.

4. If the user disagrees with the decision and wants it changed, say they can edit the code before `/next-rat`, or run `/decide-rat` if the rule should hold for the whole project.
