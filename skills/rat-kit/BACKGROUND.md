# Launching a background build

This is the only agent-specific part of the rat skills. Run `rat.py building N` before launching, so `status` shows the build.

## Claude Code

Use the Agent tool with `subagent_type: "general-purpose"` and `run_in_background: true`. Prompt:

```
Build commit <N> of rat plan <id>, "<commit title>".
Follow <rat-kit>/BUILD.md, including "Background builds only".
Plan file: <plan file>
State folder: <state folder>
Worktree, the only folder you may edit: <worktree>
User's folder, for reading docs/adr only: <repo top>
```

You get a notification when it finishes. A build counts as running only if you launched it in this conversation. After a session restart, treat any `building` commit as dead and launch it again.

## Other agents

Any agent that can run a non-interactive session in the background works. Give it the same prompt, with the worktree as its working folder:

- Codex: `codex exec --cd <worktree> "<prompt>" > <state folder>/build-N.log 2>&1 &`
- Claude Code without the Agent tool: `claude -p "<prompt>" --permission-mode acceptEdits > <state folder>/build-N.log 2>&1 &`

Then poll `rat.py status` until commit N shows `built`.
