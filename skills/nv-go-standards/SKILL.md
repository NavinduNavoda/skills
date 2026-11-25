---
name: nv-go-standards
description: Go project layout with deep modules in app/internal/modules, contract.go and doc.go rules, and Go testing. Read by nv-coding-style for Go code. Run it to apply the rules outside a flow.
disable-model-invocation: true
---

# Go standards

Applies to Go code on top of `../nv-coding-style/SKILL.md` and its `STANDARDS.md`. Tests follow `../nv-testing/SKILL.md`. A repo's own `CODING_STANDARDS.md` overrides all of them.

The layout exists so an agent or a new reader can find what a service does by reading a few small files. A module's `doc.go` and `contract.go` tell a caller everything they need. They never need to open the implementation.

## Layout

```
app/
  cmd/<service>/main.go        entry point: load config, build stores and modules, start the server
  internal/
    app/<service>/             code for one service only: handlers, routing, glue that calls modules
    modules/<name>/            deep modules: domain logic behind one interface
    store/                     store interfaces, in domain language
    store/<vendor>/            store implementations, such as store/postgres
    pkg/                       general helpers with no domain knowledge
```

Imports point one way:

| Package | May import | Must never import |
|---|---|---|
| `cmd/<service>` | everything it wires | |
| `app/<service>` | `modules`, `pkg` | `store/<vendor>`, another service's `app` |
| `modules/<name>` | `store` (interfaces), `pkg`, another module's contract | `app`, `store/<vendor>`, another module's implementation |
| `store` | `pkg`, shared domain types | `modules`, `app`, any vendor SDK |
| `store/<vendor>` | `store`, the vendor driver or SDK | `modules`, `app` |
| `pkg` | the standard library and third-party libraries | any other project package |

Only `main.go` imports `store/<vendor>` and passes the implementations into modules.

## Deep modules

A deep module hides a lot of logic behind a small interface (Ousterhout, *A Philosophy of Software Design*). A caller learns the interface and nothing else.

### When code becomes a module

- Domain logic used by more than one service, or enough logic to hide behind a few methods.
- Otherwise it stays in `app/<service>`. A module that hides nothing adds a layer and saves the reader nothing.

### Files

```
modules/order/
  doc.go           package comment only
  contract.go      the Service interface, its types, errors, Deps and New
  service.go       the unexported implementation
  <more>.go        any number of unexported files, or internal/ subpackages
  order_test.go    tests through the contract, in package order_test
  ordertest/       a fake of Service, only when more than one package needs it
```

### doc.go

Holds the package comment and the `package` line, nothing else. The comment starts with `Package <name>` and says:

1. What the module does.
2. What it hides from callers.
3. How to use it: build a `Service` with `New`, then call its methods.
4. Its concurrency guarantee. Go assumes a type is safe for one goroutine only, so state it when the `Service` is safe for concurrent use.

```go
// Package order handles placing, tracking and cancelling customer orders.
//
// It hides payment, inventory checks and persistence behind a small API.
// Callers create a Service with New and use its methods; they never need
// to touch the database or payment provider directly.
//
// All methods are safe for concurrent use.
package order
```

No other file in the package has a package comment.

### contract.go

The whole public surface of the module lives here and nowhere else:

- The `Service` interface. Each method has a doc comment with what a caller needs: what it does, side effects, preconditions, and which errors it returns. Never how it works.
- Every type the methods take or return.
- Sentinel errors a caller acts on, such as `ErrOrderNotFound`.
- `Deps`, the struct of everything the module needs: store interfaces from `internal/store`, other modules' `Service` interfaces, a clock, a logger.
- `New(deps Deps) Service`, which returns the unexported implementation.

```go
package order

type Service interface {
	// Place creates the order and charges the payment in one step.
	// It returns ErrOutOfStock when any item is unavailable.
	Place(ctx context.Context, input PlaceInput) (Order, error)
}

type Deps struct {
	Orders   store.OrderStore
	Payments store.PaymentStore
	Now      func() time.Time
}

func New(deps Deps) Service { return &service{deps: deps} }
```

The exported interface is a deliberate exception to the Go guidance that interfaces belong to the consumer. Here the interface is the module's contract and the map a reader opens first. Outside `modules/`, the usual rule applies: accept interfaces, return concrete types.

### Depth rules

- **Small contract, large implementation.** There is no method count. A method or field belongs in the contract only when a caller needs it.
- **No pass-through methods.** A method that only forwards to one store call means the module is too shallow. Put the logic in it or remove the module.
- **No vendor in the contract.** No SQL, SDK or HTTP types in `contract.go`.
- **Pull complexity down.** `New` fills sensible defaults. Callers do not set knobs the module can decide.
- **Define errors out of existence where possible.** Export only the errors a caller handles differently.
- **Modules depend on modules through `Deps`.** A module imports another module's package only for its `Service` interface and types, never its implementation. `main.go` wires them, which keeps import cycles out.

## Go conventions

- Format with `gofmt` and `goimports`. Lint with `golangci-lint`.
- `ctx context.Context` is the first parameter of every method that does I/O.
- Wrap errors with `fmt.Errorf("place order: %w", err)` and check them with `errors.Is` and `errors.As`.
- No package named `util`, `common`, `misc`, `types` or `interfaces`. Names do not repeat the package: `order.Service`, not `order.OrderService`.

## Testing

The rules are in `../nv-testing/SKILL.md`. In this layout they apply as follows:

| Layer | Test | How |
|---|---|---|
| `modules/<name>` | Yes, it holds the business logic | Through `Service` only, with in-memory fakes of the store interfaces and other modules in `Deps`. The real implementation and the `pkg` helpers it calls run. |
| `app/<service>` handlers | Status codes, redirects, cookies | `handler.ServeHTTP` with `httptest.NewRecorder`, with fake modules injected |
| `store/<vendor>` | Only what the database enforces | Against a real database: unique indexes, constraints, hand-written queries |
| `pkg` | Only logic on the nv-testing "Test" list | Otherwise covered by the module tests |
| `cmd`, `doc.go`, `contract.go` types | No | Wiring and plain data |

- Module tests use the external test package, `package order_test`, so the compiler rejects a test that reaches past the contract.
- Fakes are hand-written structs with in-memory data, not a mock library. A fake stays in the test file that uses it. It moves to `modules/<name>/<name>test/` when a second package needs it.
- Table-driven tests run each case with `t.Run`, named for the behaviour.
- No `httptest.NewServer`, because it opens a port. No `time.Sleep`. Pass a clock through `Deps`.
- CI runs `go test -race ./...`.
