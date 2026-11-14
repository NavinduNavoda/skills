# Contributing

These are the skills I use every day. Bug reports and ideas are welcome.

## Where each request goes

| You have | Do this |
| --- | --- |
| A skill did the wrong thing | Open a [bug issue](https://github.com/NavinduNavoda/skills/issues/new?template=bug.yml) |
| A change to an existing skill | Open an [idea issue](https://github.com/NavinduNavoda/skills/issues/new?template=idea.yml) |
| An idea for a new skill | Open an [idea issue](https://github.com/NavinduNavoda/skills/issues/new?template=idea.yml) before you write it |
| A typo or a small fix | Open a pull request |

For anything bigger than a small fix, open an issue first so we agree on the change before you write it.

## Writing a good issue

- **One problem per issue.**
- **Repro first.** Say what you ran, what the skill did, and what you expected. Put that before any analysis.
- **Short.** If it doesn't fit on one screen, cut it.
- **No pasted rewrites.** Describe the problem. Don't paste a whole rewritten `SKILL.md`.

Agents are welcome to help you write an issue, but you post it, so you own it. Cut it down to the repro before you post.

## Pull requests

- Follow the writing and git rules in [`AGENTS.md`](./AGENTS.md): Conventional Commit titles, one logical change per commit, no em dashes in prose.
- A new skill goes in `skills/<name>/SKILL.md` and gets a line in the skill list in [`README.md`](./README.md).
- Run `./install-to-claude.sh` and try the skill in a real session before you open the PR.
