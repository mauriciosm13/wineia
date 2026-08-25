# Testing

WineAI unit tests focus on **domain logic** and **core utilities** using **pure mocks and fakes**. CI does not run the Datastore emulator or require GCP credentials.

See [ADR 0002](./adrs/0002-unit-tests-pure-mocks.md) and [specs/coverage-gate.md](./specs/coverage-gate.md).

---

## Principles

1. **Test business rules in `domain/`** — inject fake repositories, not `Datastore*Repository`.
2. **Keep tests fast and deterministic** — no network, no real Twilio or Claude calls in unit tests.
3. **Avoid heavy imports in handler tests** — do not import `api.handlers` modules that construct Datastore clients at **module import** time.
4. **One allowed handler test** — `api.handlers.health_handler` is safe (no infrastructure side effects).

---

## Layout

```
tests/
  conftest.py           Shared fixtures
  fakes/
    repositories.py     In-memory repository fakes
  unit/
    domain/             Service tests with fakes
    core/               Utility tests
    api/                health_handler only (bootstrap)
```

---

## Running tests locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

# Lint
ruff check api core domain infrastructure tests

# Tests
pytest

# Tests with coverage (matches CI)
pytest --cov --cov-report=term-missing
```

`PYTHONPATH=.` is set in CI; locally `pyproject.toml` sets `pythonpath = ["."]`.

---

## Pytest configuration

From `pyproject.toml`:

| Setting | Value |
|---------|-------|
| `testpaths` | `["tests"]` |
| `pythonpath` | `["."]` |
| `norecursedirs` | `.git`, `.venv`, **`google-cloud-sdk`**, `.agents` |
| `addopts` | `-q`, `--strict-markers` |

**Skip `google-cloud-sdk`:** if a copy of the SDK exists in the workspace, pytest must not collect it. It is listed in `norecursedirs` and `.gitignore`.

---

## Fakes vs mocks

**Prefer fakes** implementing domain repository interfaces (see `tests/fakes/repositories.py`):

```python
from tests.fakes.repositories import FakeCustomerRepository
from domain.services import customer_service

def test_create_customer():
    repo = FakeCustomerRepository()
    result = customer_service.create_customer(repo, "+5511999999999", "Ada")
    assert result["phone"] == "+5511999999999"
```

Use `unittest.mock` only when a fake is not worth maintaining for a one-off.

---

## Handler testing rules

| Safe | Avoid (until refactored) |
|------|---------------------------|
| `from api.handlers.health_handler import handle_health` | Handlers that import `infrastructure.repositories.datastore_*` at top level |

If you need to test HTTP behavior for datastore-backed handlers, test the **domain service** the handler calls, or refactor handler wiring so Datastore is created inside the request path (factory/DI), not at import.

---

## Coverage

CI runs:

```bash
pytest --cov --cov-report=term-missing --cov-report=xml
```

Scoped sources: `domain`, `core` (see coverage spec). CI `fail_under` is **95%** (suite currently 100% on that scope).

Do not import infrastructure in tests solely to bump coverage — expand domain and core tests instead.

---

## What we do not test in unit CI

- Real Datastore read/write
- Twilio webhook signature validation (when implemented — use dedicated tests with fixed payloads)
- Cloud Tasks enqueue (integration or manual)
- End-to-end WhatsApp flows

These belong in manual QA, future integration tests, or staging — **out of MVP scope** per [MVP_SCOPE.md](./MVP_SCOPE.md).

---

## Related docs

- [ENGINEERING_MANUAL.md](./ENGINEERING_MANUAL.md)
- [GIT_WORKFLOW.md](./GIT_WORKFLOW.md) — commit type `test:` for test-only changes
