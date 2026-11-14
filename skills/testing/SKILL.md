---
name: testing
description: Decide which code gets tests and how to write them. Use when writing, adding, reviewing, or deciding on tests, or when building a feature or commit that may need them.
---

# Testing

Test the code where a bug causes harm or goes unnoticed. A file with no test is fine when none of its
code is on the "Test" list. A repo's own `CODING_STANDARDS.md` overrides this skill.

## Test

- Business rules: validation, permissions, calculations, state changes.
- Security checks: login, sessions and tokens, password handling, access control, input that reaches a
  query or a shell.
- Error mapping a caller depends on, such as a duplicate key becoming `ErrEmailTaken`.
- A fixed bug, with a test that fails without the fix.

## Skip

- Entry points and wiring: `main`, route registration, dependency setup.
- Code that only calls the standard library or a framework, such as starting a server or a health
  handler that returns 200.
- Plain data types, getters and pass-through layers.
- Template markup and copy.
- A rule already tested at another layer.

## How

- Business logic is tested with in-memory fakes of the store interfaces, with no web server and no
  database running.
- HTTP handlers are tested through the framework's test client with fakes injected. Test what a caller
  relies on: status codes, redirects, cookies.
- Store implementations are tested against a real database, only for what the database enforces:
  unique indexes, constraints, hand-written queries. CRUD that only exercises the ORM gets no test.
- Cases of one behaviour go in one table-driven test, named for the behaviour.
- Unit tests open no network ports and never sleep.
- Test files carry no header comment.
- CI runs the full suite on every PR and blocks the merge on failure.
