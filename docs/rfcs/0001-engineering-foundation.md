# RFC 0001: Engineering Foundation (M0)

**Status:** Accepted  
**Author:** WineAI team  
**Date:** 2026-08-24  
**Related:** [ADR 0001](./../adrs/0001-github-oidc-gcp.md), [ADR 0002](./../adrs/0002-unit-tests-pure-mocks.md), [coverage-gate SPEC](./../specs/coverage-gate.md)

---

## Summary

Establish the M0 engineering foundation for WineAI: automated quality checks on every PR, Docker image validation in CI, conventional commit enforcement, OIDC-based CD to a single Cloud Run production service, unit tests with pure mocks, a bootstrap coverage gate, and a lightweight documentation process (RFC / ADR / SPEC templates).

---

## Motivation

WineAI is a production WhatsApp sommelier service on GCP. Without consistent CI, deploy discipline, and testability rules, changes to messaging, recommendations, and customer data would be risky. M0 creates a repeatable quality bar and a single prod deploy path so feature milestones (M1–M7) can ship safely.

---

## Goals

- Run **pytest**, **ruff**, and **coverage** on PRs and pushes to `main`.
- Build the **Docker image in CI** without pushing (validate Dockerfile + gunicorn entrypoint).
- Enforce **Conventional Commits** on PR titles and commit messages.
- Deploy to **Cloud Run** via **GitHub OIDC** (no long-lived JSON keys) on tags `v*.*.*` and `workflow_dispatch` only.
- Test **domain** and **core** logic with **pure mocks/fakes** (no Datastore emulator in CI).
- Bootstrap a **coverage gate** on `domain` + `core` (measured 100%, CI `fail_under` 95%).
- Provide **doc templates** and this RFC-lite as the process anchor.

---

## Non-Goals

- Staging or second Cloud Run environment
- Datastore emulator in CI
- mypy (deferred)
- Per-PR changed-code coverage (deferred)
- Auto-deploy on every push to `main`

---

## Detailed Design

### Repository layout

Clean Architecture layers:

```
api/              # HTTP routing and handlers
core/             # config, queues, shared utilities
domain/           # models, services, repository interfaces
infrastructure/   # Datastore, Twilio, Claude, Cloud Tasks
```

Dependency rule: `domain` must not import `infrastructure`.

### CI workflow (`.github/workflows/ci.yml`)

Triggers: `pull_request`, push to `main`, `workflow_dispatch`.

Steps:

1. Python 3.11, install `requirements-dev.txt`
2. `ruff check api core domain infrastructure tests`
3. `pytest --cov --cov-report=term-missing --cov-report=xml`
4. Upload `coverage.xml` artifact

### Docker workflow (`.github/workflows/docker.yml`)

After tests pass, build image with `push: false` and tag `wineia:ci`. Validates Dockerfile and `gunicorn … main:app` without publishing.

### Conventional commits (`.github/workflows/conventional-commits.yml`)

- **commitlint** via `wagoid/commitlint-github-action` using `.commitlintrc.yaml`
- **Semantic PR titles** via `amannn/action-semantic-pull-request`

Allowed types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.

### CD workflow (`.github/workflows/deploy.yml`)

Triggers:

- Push tag matching `v*.*.*`
- `workflow_dispatch` (manual)

Flow:

1. Run same quality gate as CI (ruff + pytest + coverage)
2. Authenticate with GCP using **Workload Identity Federation** (`vars.WIF_PROVIDER`, `vars.WIF_SERVICE_ACCOUNT`)
3. Build and push image to Artifact Registry
4. Deploy Cloud Run service `wine-concierge` with `--no-traffic`, then shift traffic to latest revision

**No deploy on push to `main`** — the only environment is production.

### Local deploy

`./deploy.sh` builds, pushes, and deploys to the same project/region/service for operator-driven releases.

### Documentation process

| Need | Template |
|------|----------|
| Design proposal | [docs/templates/RFC.md](../templates/RFC.md) |
| Dependency / architecture decision | [docs/templates/ADR.md](../templates/ADR.md) |
| Runtime behavior | [docs/templates/SPEC.md](../templates/SPEC.md) |
| Implementation checklist | [docs/templates/TASK.md](../templates/TASK.md) |

Numbered RFCs and ADRs live under `docs/rfcs/` and `docs/adrs/`.

### Testing approach

See [ADR 0002](../adrs/0002-unit-tests-pure-mocks.md) and [TESTING.md](../TESTING.md). Domain services receive fake repositories; avoid importing handlers that construct Datastore clients at module import time.

### Coverage gate

See [specs/coverage-gate.md](../specs/coverage-gate.md). Scope: `domain` models/services + `core`. Measured 100%; CI `fail_under` 95%. Abstract repository packages are omitted. Datastore `Client` is stubbed in tests so selector/IA/recommendation services can be imported without GCP.

---

## Alternatives

| Alternative | Pros | Cons |
|-------------|------|------|
| JSON service account key in GitHub Secrets | Simple setup | Key rotation burden, leak risk |
| Deploy on every merge to `main` | Faster feedback | Unsafe for single prod environment |
| Datastore emulator in CI | Integration fidelity | Slower CI, emulator maintenance |
| Skip Docker CI build | Less CI time | Dockerfile drift undetected |

---

## Risks

| Risk | Mitigation |
|------|------------|
| OIDC misconfiguration blocks deploy | Document setup in DEPLOYMENT.md; test with workflow_dispatch |
| Low initial coverage | Bootstrap gate; raise floor as tests land |
| Accidental secrets in repo | M0 repo hygiene task; `.gitignore` for keys and SDK |

---

## Migration

Greenfield — no migration. Existing manual deploy via `deploy.sh` remains available alongside tag-based CD.

---

## Open Questions

- [ ] When to enable structured logging (replace `print` in `api/routes.py`)?
- [ ] When to add `google-cloud-tasks` to requirements and wire `CloudTasksClient` (M5)?

---

## Acceptance

- [x] CI, Docker, conventional-commits, and deploy workflows present
- [x] ADR 0001 (OIDC) and ADR 0002 (pure mocks) accepted
- [x] Coverage gate spec documented
- [x] ENGINEERING_MANUAL, TESTING, DEPLOYMENT, GIT_WORKFLOW docs added
