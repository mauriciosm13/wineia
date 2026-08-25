# SPEC: Coverage Gate

**Status:** Active  
**Owner:** WineAI engineering  
**Related RFC:** [RFC 0001 — Engineering Foundation](../rfcs/0001-engineering-foundation.md)  
**Last updated:** 2026-08-24

---

## Overview

CI enforces a **bootstrap coverage gate** using **pytest-cov**. The gate protects domain and core business logic from untested regressions while the test suite grows. It is intentionally narrower than full-repo coverage.

---

## Responsibilities

| Component | Role |
|-----------|------|
| `pytest-cov` | Collect coverage during test runs |
| `pyproject.toml` `[tool.coverage.*]` | Define sources, omit paths, `fail_under` |
| `.github/workflows/ci.yml` | Run pytest with `--cov` on every PR |
| `.github/workflows/deploy.yml` | Same gate before production deploy |

---

## Scope

**Included in coverage measurement:**

- `domain/` models and services (including IA, selector, recommendation job)
- `core/` config, logging, queues, utilities

**Excluded from the percentage gate:**

- `domain/repositories/` abstract interfaces (`pass` bodies)
- `api/` handlers that construct Datastore at import (health handler is unit-tested, not in the %)
- `infrastructure/` — GCP adapters; Datastore `Client` is stubbed in `tests/conftest.py` so domain imports do not need credentials

**Explicitly not used:** Go-style changed-code covercheck or diff-only gates (deferred).

---

## Configuration

From `pyproject.toml`:

```toml
[tool.coverage.run]
source = ["domain", "core"]
omit = [
  "*/google-cloud-sdk/*",
  "*/.venv/*",
  "domain/repositories/*",
]
branch = true

[tool.coverage.report]
fail_under = 95
show_missing = true
skip_empty = true
```

CI command:

```bash
pytest --cov --cov-report=term-missing --cov-report=xml
```

Dev dependencies: `pytest-cov` in `requirements-dev.txt`.

---

## Bootstrap policy

1. **Measure** after the unit suite (`domain` services/models + `core`).
2. **Baseline** — suite is **100%** on scoped files. CI `fail_under` is **95%**.
3. **Fail on regression** — CI fails if scoped coverage drops below `fail_under`.
4. **Next** — add handler tests (with fakes) and drop remaining omits when interfaces gain real code.

Changed-code coverage (only lines touched in a PR) is **deferred** until baseline is stable and tooling is chosen.

---

## Data Flow

```
PR / tag push
  → pip install requirements-dev.txt
  → pytest --cov
  → coverage.py aggregates domain + core
  → fail_under check
  → upload coverage.xml artifact (CI job)
```

---

## Errors

| Condition | Result |
|-----------|--------|
| Coverage &lt; `fail_under` | CI job fails; merge blocked |
| Missing pytest-cov | Install step fails |
| Tests fail | Coverage step not reached / job fails |

---

## Metrics

| Metric | Source | Use |
|--------|--------|-----|
| Line coverage % | `coverage.xml` / terminal report | Gate |
| Missing lines | `--cov-report=term-missing` | Find gaps |

---

## Logs

Coverage output appears in GitHub Actions job log under “Run tests with coverage”. Artifact `coverage.xml` retained per workflow run.

---

## Tracing

Not applicable.

---

## Security

Coverage reports contain file paths only; no secrets. Artifacts are internal to GitHub Actions.

---

## Performance

Full suite target: under a few minutes on `ubuntu-latest`. No emulator or network calls in unit tests.

---

## Testing

- Verify locally: `pytest --cov`
- Confirm gate: temporarily lower coverage in a branch and expect CI failure
- Health handler test validates minimal `api/` inclusion without Datastore imports

See [TESTING.md](../TESTING.md) and [ADR 0002](../adrs/0002-unit-tests-pure-mocks.md).
