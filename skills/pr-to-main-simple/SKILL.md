---
name: pr-to-main-simple
description: Commit everything, rebase on main, push, and open a title-only PR into main.
disable-model-invocation: true
model: claude-haiku-5-5
---

# PR to main, simple

Typing this skill is the user's explicit request to target `main`, so it overrides the "never target `main`" default in `../nv-git-workflow/SKILL.md`.

## Steps

1. **Check what gets committed.** Run `git status --short`. If it lists untracked files (`??`) that the chat didn't create on purpose, such as `.env`, keys, logs or scratch files, list them and ask the user which to include before going on.

2. **Generate three strings, once.** Work from the chat history and `git status --short` plus `git diff HEAD --stat`:
   - `BRANCH`: `<type>/<short-description>`, lowercase kebab-case, 1 to 4 words. Only needed when on `main`.
   - `MSG`: the commit message, `<type>: <short description>`, no attribution trailer.
   - `TITLE`: the PR title in the same format, describing the whole change.

   Write `MSG` and `TITLE` per `../nv-writing-style/SKILL.md` if it is installed.

3. **Run these in order.** Stop at the first failing command and report its output.

   ```sh
   if [ "$(git branch --show-current)" = main ]; then git switch -c "$BRANCH"; fi
   git add -A && git commit -m "$MSG"   # skip when there is nothing to commit; leave out files the user excluded in step 1
   git pull --rebase origin main
   git push --force-with-lease -u origin HEAD   # the rebase rewrites an already-pushed branch
   gh pr create --base main --title "$TITLE" --body ""
   ```

4. **Report** the PR URL.
