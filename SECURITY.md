# Security policy

## Supported versions

Only the latest commit on `main` is supported. skills.sh installs from `main`, so a fix reaches users when they run `npx skills update`.

## What counts as a vulnerability

- `skills/start-relay/scripts/relay.py` writing, committing or deleting anything outside what [`SCRIPT.md`](./skills/start-relay/SCRIPT.md) lists, or running anything other than `git`.
- A skill that tells the agent to run a command, push, reach the network or touch files outside the user's repo when the skill does not say so.
- A skill that reads a path outside its own folder or its sibling skill folders.
- A way for text in a user's repo, such as a plan file or an ADR, to make a relay step run commands the skill does not list.

A skill giving bad advice, or the agent ignoring a skill, is a bug, not a vulnerability. Open a [bug issue](https://github.com/NavinduNavoda/skills/issues/new?template=bug.yml) for those.

## Reporting

Report privately through [GitHub's private vulnerability reporting](https://github.com/NavinduNavoda/skills/security/advisories/new). Don't open a public issue.

Include the skill, the commit you installed from, your agent and model, and the steps that show the problem.

I reply within 7 days. Once a fix is on `main`, I publish the advisory and credit you, unless you ask not to be named.
