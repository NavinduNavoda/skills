# Classifying the user's edits

Run this when `finalize` reports `changed: true`, or when the user answered a question differently from the default a builder used.

## Claude Code

Use the Agent tool with `model: "haiku"` and `subagent_type: "general-purpose"`, in the foreground. Prompt:

```
A developer reviewed commit <N> and edited it. Commit <N+1> was already built on the
unedited version. Decide how commit <N+1> must change.

Developer's edits to commit <N>: read <user diff path>
Commit <N+1> as built: read <patch path>
Changed answers to open questions: <answers, or "none">

Reply with one word on the first line, then one sentence of reason:
NONE  - the edits don't affect anything commit <N+1> touches or uses.
SMALL - commit <N+1> needs a few local fixes, such as a renamed function or a changed argument.
BIG   - the edits change the approach, data shape or interfaces commit <N+1> is built on,
        so patching would touch most of it.
When unsure between two answers, pick the bigger one.
```

Other agents: send the same prompt to the smallest fast model available. With no subagent, judge it yourself with the same three definitions.
