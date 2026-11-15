# Rules for every relay step

Every relay skill and every builder follows these. A repo's own `AGENTS.md`, `CLAUDE.md` or `CONTRIBUTING.md` wins where it disagrees.

## Decisions

- Decide anything with a sensible default yourself and build with it. Record each choice as a `Decision:` line with its reason, so the user can override it in review.
- Ask the user only for:
  - a new dependency,
  - an action that is hard to undo or reaches outside the repo,
  - a choice that goes against the user's instructions or an ADR in `docs/adr/`.
- Put all questions in one round, never one at a time.

## Git

- Follow `../nv-git-workflow/SKILL.md` for branch names and commit titles if it is installed. Otherwise match the repo's recent history.
- Never push. The user decides when to push and open a pull request.
