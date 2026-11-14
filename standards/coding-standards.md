# Coding standards

Applies to every repo when writing or reviewing code. A repo's own `CODING_STANDARDS.md` overrides this file where they disagree.

## Architecture and loose coupling

Every service is split into layers, and dependencies point in one direction only: from the outside (HTTP, CLI, entry point) inward to business logic, and from business logic to abstract interfaces. Business logic never knows which web framework or database is behind it.

| Layer | Does | Must never |
|---|---|---|
| Entry point | Load config, build every dependency, inject them, start and stop the server | Contain business rules |
| HTTP layer | Parse and validate input, call business logic, map results and errors to responses | Contain business rules or database queries |
| Business logic | Apply the rules of the domain using plain values | Import the web framework or a database driver |
| Store interfaces | Describe what the app needs from storage, in domain language | Mention the vendor |
| Store implementation | Talk to the actual database or external API | Be imported by anything except the entry point |
| Shared types | Plain data structures used by every layer | Import any other project module |

- **Depend on interfaces, not implementations.** Business logic receives a `UserStore` interface, never a `PostgresUserStore`.
- **One composition root.** Only the entry point (or app factory) chooses concrete implementations and wires them together.
- **Name the vendor in exactly one place.** Only the store implementation imports a database driver or cloud SDK. Changing a database means adding one implementation and changing the wiring, nothing else.
- **Pass dependencies explicitly.** No global mutable state, no singletons reached from deep inside business logic, no reading environment variables outside the config module.
- **Keep the database model separate from the domain model.** Row or document mappings live in the store layer. Domain types carry no ORM annotations.

Coupling test: if you cannot unit test a piece of business logic without starting a web server or a database, the layers are mixed.

## API conventions

- JSON APIs live under a versioned prefix, `/api/v1/...`. A breaking change to a request or response shape goes into a new version, never the existing one.
- URLs are kebab-case: `/api/v1/payment-records`.
- JSON field names are snake_case. Timestamps are RFC 3339 in UTC. IDs are UUID strings.
- Use the right HTTP method for each operation.
- List endpoints are paginated from the start, with a documented maximum page size.
- Every service exposes `GET /healthz` (liveness, never touches dependencies) and `GET /readyz` (readiness, checks dependencies with a short timeout).
- Error responses carry an error type and message, plus an error code when there are many error types.

## Data

Every table, collection or entity carries these five audit fields, spelled exactly like this:

| Field | Type | Meaning |
|---|---|---|
| `created_at` | Timestamp (UTC) | When the record was created |
| `created_by` | String, nullable | User or service ID that created it |
| `updated_at` | Timestamp (UTC) | When it last changed |
| `updated_by` | String, nullable | Who last changed it |
| `is_removed` | Boolean, default false | Soft-delete flag |

Valuable domain data is soft deleted: removal sets `is_removed = true`. Transient or high-volume data, such as logs, may be hard deleted to keep the database small.

## Configuration and secrets

- Services read configuration from environment variables and load secrets from GCP Secret Manager at startup, through one config module, validated once. A missing or invalid required value stops the process with a clear error.
- Variable names are UPPER_SNAKE_CASE (`DATABASE_URL`, `HTTP_PORT`).
- Local values live in `.env`, which is gitignored. `.env.example` is committed with every variable name and a dummy value.
- Production secrets live in the secret manager, never in the repository, CI logs or chat.
- A committed credential is leaked: rotate it first, then remove it. Rewriting history does not un-leak it.

## Logging

- Structured JSON on stdout, one event per line, key-value fields rather than formatted strings.
- One logger module per service, configured at startup before anything that can fail.
- Every request gets a request ID, attached to every log line for that request and returned in the `X-Request-ID` header.
- Levels: DEBUG for development detail, INFO for lifecycle events, WARN for recoverable problems, ERROR for failed requests and operations.
- Handle an error once: return it or log it, not both.
- Never log passwords or their hashes, tokens, cookies, API keys, encryption keys, personal data beyond an ID, or request bodies of auth endpoints. When unsure, leave the field out.

## Testing

See the `testing` skill (`~/.agents/skills/testing/SKILL.md`).
