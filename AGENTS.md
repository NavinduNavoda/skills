# Working on this repo

This repo ships agent skills through skills.sh (`npx skills add NavinduNavoda/skills`). skills.sh copies only the folders under `skills/`, so everything a skill needs lives in a skill folder.

## Skill kinds and names

- **Flow skills** belong to one way of building software. Name them `<verb>-<flow>`: `start-relay`, `next-relay`. The flow's shared files live in its `start-<flow>` skill, and the other skills of the flow reach them at `../start-<flow>/`.
- **Shared skills** are building blocks any flow can read. Name them `nv-<name>`: `nv-coding-style`, `nv-testing`.
- **Converter skills** turn something from the chat into a file. Name them `to-<artifact>`: `to-adr`. Any flow can use them, like `nv-` skills.
- A flow may read `nv-` and `to-` skills. A flow never reads another flow's skills.

## Skill rules

- Each skill is `skills/<name>/SKILL.md`, with a `name` that matches the folder and a `description` that says what it holds.
- Every skill sets `disable-model-invocation: true`. Skills run only when a user types them or a flow reads them, so they never compete with a user's own skills.
- A skill references only files in its own folder or in a sibling skill folder (`../nv-testing/SKILL.md`). Never `~/` paths.
- A flow skill that needs `start-<flow>` says to stop and ask the user to install it when the folder is missing. A flow treats `nv-` and `to-` skills as optional: when one is missing, it follows the repo's own rules and the code around it.
- A repo's own `CODING_STANDARDS.md`, `AGENTS.md`, `CLAUDE.md` or `CONTRIBUTING.md` wins over any `nv-` skill. Every shared skill says so.
- Every skill has a line in the skill list in `README.md`.
- Scripts use the language's standard library only. `SCRIPT.md` in the skill says what the script runs, what it writes and what it deletes.

## Checks

- Relay script tests: `python3 -m unittest test_relay.py` from `skills/start-relay/scripts/`.
- After adding, renaming or removing a skill, run `./install-to-claude.sh` and try the skill in a real session.

## Writing and git

Follow `skills/nv-writing-style/SKILL.md` for prose, including `SKILL.md` files, and `skills/nv-git-workflow/SKILL.md` for branches, commits and pull requests.
