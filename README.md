# skills

My agent skills for Claude Code, plus the global `AGENTS.md` and coding standards they rely on.

## Install

```bash
git clone git@github.com:NavinduNavoda/skills.git
cd skills
./install-to-claude.sh
```

The script symlinks each folder in `skills/` into `~/.claude/skills/` and links `AGENTS.md` to `~/.claude/CLAUDE.md`. That replaces your global `CLAUDE.md` with this repo's, so read [`AGENTS.md`](./AGENTS.md) first. The script moves any real file it would replace to `<name>.bak.<timestamp>`.

Because the installed skills are symlinks, `git pull` updates them. Re-run the script after a skill is added, removed or renamed. It also deletes broken links that point into this repo. Set `CLAUDE_CONFIG_DIR` to install somewhere other than `~/.claude`.

To remove the links and move your backed-up `CLAUDE.md` back:

```bash
./uninstall-from-claude.sh
```

## Skills

### Rat workflow

These skills build a feature as a chain of small commits. You review commit N while a background agent builds commit N+1 in a separate worktree.

- [`start-rat`](./skills/start-rat/SKILL.md): start a feature and plan it as small commits.
- [`next-rat`](./skills/next-rat/SKILL.md): finalize the commit under review and bring in the next one, adapted to your edits.
- [`why-rat`](./skills/why-rat/SKILL.md): explain a decision in the current plan in depth, for a junior developer.
- [`decide-rat`](./skills/decide-rat/SKILL.md): turn a decision from chat into a numbered ADR in `docs/adr/`.
- [`ask-rats`](./skills/ask-rats/SKILL.md): say which rat skill to run next, based on the plan's state.
- [`rat-kit`](./skills/rat-kit/SKILL.md): shared scripts and rules for the skills above. You don't run it directly.

### Code quality

- [`coding-style`](./skills/coding-style/SKILL.md): line-level code style for any language. The model loads it when writing or reviewing code.
- [`testing`](./skills/testing/SKILL.md): decide which code gets tests and how to write them. The model loads it when tests come up.
- [`spec-review`](./skills/spec-review/SKILL.md): review a diff against the repo's coding standards and against the issue it came from, in two parallel subagents.

### Learning

- [`teach`](./skills/teach/SKILL.md): teach you a topic over several sessions, with progress saved in the workspace.

## Contributing

See [`CONTRIBUTING.md`](./CONTRIBUTING.md).

## License

[MIT](./LICENSE)
