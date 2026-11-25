# skills

Agent skills for building software in small, reviewable commits. They install with [skills.sh](https://skills.sh) into Claude Code, Codex and other agents.

## Install

Install every skill from the latest release:

```bash
npx skills add NavinduNavoda/skills#latest -s '*'
```

Add `-g` to install for every project instead of the current one. If you pick skills one by one, install the relay skills together and in the same scope, because `next-relay`, `finish-relay`, `why-relay` and `status-relay` use files from `start-relay`, and `finish-relay` also uses `next-relay`. To upgrade, run the install command again. Leave out `#latest` to install the newest commit on `main` instead.

Every skill runs only when you type it or a flow reads it. None of them loads on its own, so they don't override your own skills or rules.

## Skills

### Relay flow

You review commit N while a background agent builds commit N+1 in a separate worktree. When you approve N, the agent brings in N+1, adapted to any edits you made.

- [`start-relay`](./skills/start-relay/SKILL.md): plan a feature as small commits, build commit 1 and start commit 2 in the background. It also holds the files the other relay skills use.
- [`next-relay`](./skills/next-relay/SKILL.md): commit the one under review and bring in the next, adapted to your edits.
- [`finish-relay`](./skills/finish-relay/SKILL.md): commit the one under review, bring in the built one, then build and commit every remaining commit without review stops.
- [`why-relay`](./skills/why-relay/SKILL.md): explain a decision in the current plan in depth, for a junior developer.
- [`status-relay`](./skills/status-relay/SKILL.md): say which relay step to run next, based on the plan's state.

`start-relay` runs a Python script, `relay.py`. It uses the standard library only, makes no network calls, and runs only `git`. [`SCRIPT.md`](./skills/start-relay/SCRIPT.md) lists what it writes and deletes.

### Shared

Flows read these when they are installed. You can also run them directly.

- [`nv-coding-style`](./skills/nv-coding-style/SKILL.md): line-level code style, plus architecture, API, data, config and logging standards.
- [`nv-testing`](./skills/nv-testing/SKILL.md): which code gets tests and how to write them.
- [`nv-go-standards`](./skills/nv-go-standards/SKILL.md): Go project layout, deep modules with `doc.go` and `contract.go`, and Go testing. `nv-coding-style` reads it for Go code.
- [`to-adr`](./skills/to-adr/SKILL.md): turn a decision from chat into a numbered ADR in `docs/adr/`.
- [`nv-git-workflow`](./skills/nv-git-workflow/SKILL.md): branch names, Conventional Commits and pull request rules.
- [`nv-writing-style`](./skills/nv-writing-style/SKILL.md): plain, specific prose for commits, pull requests, plans and docs.

A repo's own `CODING_STANDARDS.md`, `AGENTS.md`, `CLAUDE.md` or `CONTRIBUTING.md` wins over the shared skills.

### Standalone

Run these directly. No flow reads them.

- [`bro-please`](./skills/bro-please/SKILL.md): explain a snippet, file or concept in the current codebase in plain language.
- [`research-about`](./skills/research-about/SKILL.md): research a topic on the web and write it up as linked HTML pages in `docs/research/`.
- [`pr-to-main-simple`](./skills/pr-to-main-simple/SKILL.md): commit everything, rebase on `main`, push and open a title-only pull request into `main`.

## Working on the skills

`./install-to-claude.sh` symlinks each folder in `skills/` into `~/.claude/skills/`, so edits in your clone apply at once. `./uninstall-from-claude.sh` removes the links. See [`AGENTS.md`](./AGENTS.md) for the repo's rules.

## Contributing

See [`CONTRIBUTING.md`](./CONTRIBUTING.md).

## License

[MIT](./LICENSE)
