---
name: nv-git-workflow
description: Branch names, Conventional Commit messages and pull request rules. Relay builds read it. Run it to apply the rules outside a flow.
disable-model-invocation: true
---

# Git workflow

A repo's own `AGENTS.md`, `CLAUDE.md` or `CONTRIBUTING.md` wins where it disagrees.

## Branches

- Start from `main` unless the user names another base.
- Name them `<type>/<short-description>` with type `feat fix chore docs refactor test ci`, lowercase kebab-case, 1 to 4 words, no names, dates or versions.

## Commits

- Conventional Commits: `<type>: <short description>`, imperative, lowercase, no trailing full stop.
- One logical change per commit. Formatting-only changes get their own `chore:` commit.
- Add a body when the diff doesn't show why.
- Add a ticket reference only when asked.
- No `Co-Authored-By` trailer or other AI attribution.

## Pull requests

- Never merge into `main` or push to it. Open a pull request and let the user merge it.
- The title uses the commit format.
- Leave the body empty unless another skill sets it: `gh pr create --title "<title>" --body ""`. No "Generated with" line.
- After a merge, delete the branch on the remote and locally: `gh pr merge --delete-branch`. Never delete `main`.
