---
name: bro-please
description: Explain a piece of code (usually a selected snippet, a file, a function, or a concept in the current codebase) in plain, easy-to-understand language. Use when the user types /bro-please, or asks "what does this do", "explain this", "help me understand this code".
disable-model-invocation: true
argument-hint: "[question or code reference — optional if code is selected in the IDE]"
---

# Bro, please explain

The user wants to *understand* something — usually a code snippet they selected in their editor. Your job is to be the patient friend who knows the codebase and explains it clearly. Don't change any code unless they ask.

## 1. Figure out what they're asking about

Check, in this order:
1. **IDE selection** — if the conversation has a selected code range / opened file from the IDE, that's the target.
2. **Arguments** — `$ARGUMENTS` may be a question, a file path, a `file:line` reference, a function/class name, or pasted code.
3. **Recent context** — something just discussed in the conversation.

If it's still unclear what they mean, ask one short question. Otherwise just go.

## 2. Investigate before explaining

Don't explain the snippet in isolation. Read the codebase enough to answer *accurately*:
- Read the surrounding file (imports, the enclosing function/class).
- Look up definitions of the functions, classes, types, and config the snippet uses (grep / read them).
- Find where it is called from, so you can say *why* it exists and *when* it runs.
- For library/framework calls, explain what that call does in this context. If unsure about an API, check the installed source or docs rather than guessing.
- For math / ML / algorithm code, figure out the shapes, units, and the idea behind it.

Never invent behavior. If something can't be determined from the code, say so.

## 3. Answer in an understandable way

Structure (skip sections that don't apply — short code gets a short answer):

**TL;DR** — 1–2 sentences: what this does and why it's here, in plain words.

**Walkthrough** — go through the code in logical chunks (not necessarily every line). For each chunk: what it does + why. Quote the small bit of code you're talking about, and reference other places as `path/to/file.py:42`.

**Example / mental model** — when it helps, trace through with a tiny concrete example (sample input → what each step produces → output), or give an analogy. For tensors/arrays, show the shapes at each step.

**How it fits in** — who calls it, what it feeds into, where it sits in the bigger flow. A small ASCII diagram is welcome if the flow is non-trivial.

**Gotchas** — anything subtle, surprising, or easy to misread (edge cases, side effects, mutation, ordering, off-by-one, hidden defaults). Mention real bugs if you spot them, but don't fix them unprompted.

## Style

- Friendly and casual, like explaining to a teammate — but clarity over jokes.
- Plain language first; when a technical term is needed, define it in a few words the first time.
- Explain the *why*, not just the *what*.
- Short paragraphs and bullets. No walls of text.
- Match depth to the question: a one-liner question gets a focused answer, "explain this whole module" gets the full treatment.
- End by offering one natural next step (e.g. "want me to go deeper into X?") — one line, not a list.
