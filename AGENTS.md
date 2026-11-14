## Writing

For prose only (replies, commits, PRs, comments, docs), not code or quoted text. Reread commit messages, PR bodies and docs against these before committing.

- Say what a thing does, with the mechanism or a number. Cut sentences that could fit any project.
- Plain words: "use" not "leverage", "is" not "serves as", "to" not "in order to". No delve, crucial, robust, seamless, surface, primitive.
- Active voice, one idea per sentence, whole sentences. No arrows or fragments.
- No em or en dashes. Use a period or a comma.
- No filler, stacked hedges, adverbs where a verb or number fits, or chatbot lines like "Great question".

## Decisions

- Decide anything with a sensible default yourself and do it. In the reply, list each decision in one
  line with its reason, so the user can override it in review.
- Ask only for: a new dependency, an action that is hard to undo or reaches outside the repo, or a choice
  that goes against the user's instructions or an ADR. Put these in one round.

## Git

- **Branches:** start from `main` unless the user names another base. Name them `<type>/<short-description>` with type `feat fix chore docs refactor test ci`, lowercase kebab-case, 1 to 4 words, no names, dates or versions.
- **Commits:** Conventional Commits, `<type>: <short description>`, imperative, lowercase, no trailing full stop. One logical change per commit, and formatting-only changes get their own `chore:` commit. Add a body when the diff doesn't show why. Add a ticket reference only when asked.
- **No Claude attribution:** no `Co-Authored-By` trailer in commits, no "Generated with Claude Code" line in PRs.
- **Never merge into `main` or push to it.** Open a PR and let the user merge it.
- **PRs:** title in commit format. When no skill sets the body, leave it empty (`gh pr create --title "<title>" --body ""`).
- **After merging a PR,** delete its branch on origin and locally (`gh pr merge --delete-branch`). Never delete `main`.

## Coding standards

When writing or reviewing code, follow the line-level style below. Read `~/.agents/standards/coding-standards.md` before designing modules, APIs, data access or logging, and the `testing` skill before writing tests. A repo's own `CODING_STANDARDS.md` overrides all of them.

@~/.agents/skills/coding-style/SKILL.md
