---
name: nv-coding-style
description: Line-level code style for any language, plus architecture, API, data, config and logging standards. Relay builds read it. Run it to apply the style outside a flow.
disable-model-invocation: true
---

# Coding style

How code reads line by line, in any language. Read `STANDARDS.md` in this folder before designing modules, APIs, data access, configuration or logging. Tests follow `../nv-testing/SKILL.md` if it is installed. For Go code, also read `../nv-go-standards/SKILL.md`. A repo's own `CODING_STANDARDS.md` overrides all of them.

The measure behind every rule is **reader load**: how many layers a reader must trace and how much state they must hold to answer "where does this value come from?" and "what can change it?".

## Conditionals

- **Guard clauses first.** Handle the failure or empty case at the top and return early. The main path sits at the lowest indentation. After a branch that returns, continue at the outer level with no `else`.
- **Ternary for one value.** When one condition decides the value or state of a single variable and the whole statement fits on one line of about 100 characters, use a ternary:

  ```
  title = string.IsNullOrEmpty(command.Title) ? string.Empty : command.Title
  ```

  This replaces "assign a default, then override it in an `if`". A ternary holds one condition and two plain values. A choice between three or more values is a `switch` expression or a lookup map. Anything longer or with side effects is an `if`/`else`.
- **Braces on every body.** The one exception is a guard that fits on one line, written on that same line: `if (pre == null) continue;`.

## Names

- **Full words.** `response`, `unitOfWork`, `extensionDeleteResult`. The allowed short forms are `id`, `url`, `db`, `dto`, loop indices, and the domain's own acronyms (`AD`, `LDAP`, `UPN`, `DN`).
- **Idiomatic short names stay short.** When the language's own convention uses a short name, use that name. In Go that means `ctx`, `err`, `ok`, `w`, `r`, `t`, `tx`, and one- or two-letter receivers. In C# it means `e` in event handlers. Full words apply to names the convention leaves to you.
- **Spelled right.** A misspelled identifier (`UserPrincipleName`, `Pannel`) is a defect. Fix it in the change that touches it.
- **Booleans read as a question:** `isDeleted`, `hasAccount`, `canRetry`.

## Functions

- **About 40 lines at most.** Past that, split the function into steps named for what they do. A longer function needs a reason the reviewer can see.
- **A block that needs a label becomes a function.** `// create AD user` above ten lines becomes `CreateAdUser(...)`.
- **Inline one-caller wrappers** and pass-through layers that rename a call without hiding anything.
- **Prefer pure functions.** Return values over mutating arguments. Keep state in the smallest scope: a local over a field, a field over module state.

## Variables and types

- **Infer the type when the right-hand side shows it** (`var user = new User()`, `x := parse(s)`). Spell the type out when it does not.
- **Declare a variable right before its first use.**
- **Validate at the edges, trust inside.** Input from HTTP, config, files, and external APIs is checked where it enters. Code past that point trusts its types and carries no defensive null checks or try/catch for states that cannot happen.
- **Reach the right type instead of casting to silence the compiler.** A cast is fine right after a check that proves it.

## Errors

- **Catch only what you can handle or translate:** into a domain error, an HTTP status, or a rollback. Everything else bubbles up.
- **Wrap with a specific type.** When an exception must be wrapped, use a named exception type with the original as the inner exception, never the base `Exception`.

## Comments

- **None by default.** Rename, extract a function, or add a type instead.
- **Allowed:** license headers, doc comments on APIs other modules import (not `internal/`), links to
  issues or vendor docs for constraints the code cannot express, and tooling directives.
- **`WHY:` lines are review notes, not comments.** The relay flow adds them for the reviewer and its script
  removes them before each commit.

## Changes

- **Smallest diff that solves the problem.** Delete dead code and redundant checks first, then add. Build for the cases the ticket has, not imagined ones.
- **Lines wrap at 120 characters.** A long call puts one argument per line.
- **Match the surrounding file.** For anything this skill does not cover, follow the language's official conventions, then the file around you.
