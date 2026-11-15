---
name: nv-adr
description: Turn a decision the user made in chat into a numbered Architecture Decision Record in docs/adr/.
disable-model-invocation: true
argument-hint: "The decision, or leave empty to use the last one from chat"
---

ADRs hold decisions that should outlive the current feature. Every relay build reads `docs/adr/` first and follows it.

1. **Find the decision** in the argument or the recent chat. If it's only about this feature, suggest recording it in the plan's Decisions section instead and stop unless the user still wants an ADR.

2. **Number it.** Next number after the highest file in `docs/adr/`, four digits: `docs/adr/0007-use-zod-for-input-validation.md`. Create the folder if missing.

3. **Write it** in this format, short and specific to this codebase:
   ```markdown
   # 7. Use zod for input validation

   Date: YYYY-MM-DD
   Status: Accepted

   ## Context
   <the problem and the forces at play, two to five sentences>

   ## Decision
   <what we do, stated as a rule a builder can follow>

   ## Consequences
   <what gets easier, what gets harder, what code must change>
   ```
   If it replaces an older ADR, set the old one's Status to `Superseded by 0007` and link both ways.

4. **Show the draft** and let the user adjust it.

5. **Commit it on its own**, so it never mixes with the commit under review: `git add docs/adr && git commit -m "docs: add ADR 0007 use zod for input validation" -- docs/adr`. The relay script ignores `docs/adr/` when it compares commits.

6. If a relay plan is active, add a line to its Decisions section linking the ADR. If the commit under review breaks the new rule, tell the user. `/next-relay` will treat their fix as an edit.
