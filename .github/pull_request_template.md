## What and why

<!-- What this changes and why. Link the issue: Closes #123 -->

## Checks

- [ ] Each changed skill references only its own folder or a sibling skill folder, never `~/` paths.
- [ ] New or renamed skills have a line in the `README.md` skill list.
- [ ] I ran `./install-to-claude.sh` and tried the changed skills in a real session.
- [ ] If `relay.py` changed: `python3 -m unittest test_relay.py` passes in `skills/start-relay/scripts/`, and `SCRIPT.md` still lists what it writes and deletes.
