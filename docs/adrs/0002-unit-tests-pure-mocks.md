# ADR 0002: Unit Tests with Pure Mocks (No Datastore Emulator)

**Status:** Accepted  
**Date:** 2026-08-24  
**Deciders:** WineAI team  
**Related RFC:** [RFC 0001 — Engineering Foundation](../rfcs/0001-engineering-foundation.md)

---

## Context

WineAI persists customers and recommendation data in **Google Cloud Datastore** (Firestore in Datastore mode). CI runs on every PR with no GCP project credentials and must stay fast and deterministic.

Options for testing code that touches persistence:

1. **Pure mocks/fakes** — in-memory fake repositories implementing domain interfaces
2. **Datastore emulator** — local or CI-provisioned emulator
3. **Integration tests against a dev project** — real Datastore with test data

The domain layer is designed with repository interfaces so business rules can be tested without cloud dependencies.

---

## Decision

Use **pure mocks and fakes** for unit tests in CI. Do **not** require the Datastore emulator for the default test suite.

- Fakes live under `tests/fakes/` (e.g. in-memory customer repositories)
- Domain services are tested by injecting fakes, not `DatastoreCustomerRepository`
- Handler tests import only handlers that do **not** construct Datastore clients at module import time (e.g. `health_handler` is allowed; customer handlers that import datastore repos at top level should be tested via domain layer until refactored)

Integration tests against a real project or emulator are **out of scope** for M0 and deferred until explicitly requested.

---

## Consequences

### Positive

- Fast, hermetic CI without GCP credentials
- Forces clear repository boundaries in domain
- No emulator download or startup in GitHub Actions

### Negative

- Fakes can drift from real repository behavior if not updated together
- Datastore query/index edge cases may only appear in manual or future integration tests

### Neutral

- `google-cloud-sdk` directory is excluded from pytest collection (`norecursedirs` in `pyproject.toml`)
- `.gitignore` lists `google-cloud-sdk` — accidental SDK copies should not be committed

---

## Alternatives

| Alternative | Why not chosen |
|-------------|----------------|
| Datastore emulator in CI | Slower, heavier setup; not needed for current domain coverage |
| `@patch` on google.cloud.datastore everywhere | Brittle; hides interface design issues |
| Skip repository tests entirely | Unacceptable for customer/messaging rules |

---

## Tradeoffs

We optimize for **speed and layer purity** over **storage fidelity** in unit tests. When a bug is emulator-specific, add a targeted integration test or contract test — not a default CI dependency.

---

## Testing guidelines

See [TESTING.md](../TESTING.md):

- `testpaths = ["tests"]`
- Prefer testing `domain/services/*` with fakes
- Avoid `from api.handlers.customer_handler import …` if that module instantiates Datastore at import

---

## References

- [TESTING.md](../TESTING.md)
- [specs/coverage-gate.md](../specs/coverage-gate.md)
