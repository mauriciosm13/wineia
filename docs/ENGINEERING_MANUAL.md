# WineAI Engineering Manual

Index of engineering documentation for the WineAI backend. Use this as the entry point for process, architecture, and operations — not an exhaustive gateway-style bible.

---

## Product and planning

| Document | Purpose |
|----------|---------|
| [ROADMAP.md](./ROADMAP.md) | Milestones M0–M7, checkboxes, success criteria, Engineering Rule |
| [MVP_SCOPE.md](./MVP_SCOPE.md) | What ships first vs deferred (analytics, emulator, second env, k8s) |

---

## Architecture and agents

| Document | Purpose |
|----------|---------|
| [../AGENTS.md](../AGENTS.md) | Agent/AI contributor guide — layers, rules, GCP patterns |
| [../agent.md](../agent.md) | Original architecture notes (human-oriented) |
| [../README.md](../README.md) | Product overview and quick links |

**Layers:** `api/` → `domain/` → `infrastructure/`, with shared `core/`. Domain must not import infrastructure.

---

## Process templates

Copy and number new documents under `docs/rfcs/`, `docs/adrs/`, or `docs/specs/`.

| Template | Use when |
|----------|----------|
| [templates/RFC.md](./templates/RFC.md) | Proposing a design or process change |
| [templates/ADR.md](./templates/ADR.md) | Recording a decided dependency or architecture choice |
| [templates/SPEC.md](./templates/SPEC.md) | Describing runtime behavior, APIs, ops |
| [templates/TASK.md](./templates/TASK.md) | Breaking work into steps with acceptance criteria |

**Engineering Rule (from roadmap):** every milestone needs RFC (lite OK), spec for new behavior, ADR for new deps, tests, docs. No feature complete until the quality gate passes.

---

## Accepted RFCs and ADRs

| ID | Title |
|----|-------|
| [rfcs/0001-engineering-foundation.md](./rfcs/0001-engineering-foundation.md) | M0 CI, Docker CI, conventional commits, OIDC CD, docs process |
| [adrs/0001-github-oidc-gcp.md](./adrs/0001-github-oidc-gcp.md) | Workload Identity Federation — no JSON keys |
| [adrs/0002-unit-tests-pure-mocks.md](./adrs/0002-unit-tests-pure-mocks.md) | Unit tests with fakes — no Datastore emulator |

---

## Specs

| Spec | Topic |
|------|-------|
| [specs/coverage-gate.md](./specs/coverage-gate.md) | pytest-cov scope, bootstrap `fail_under`, deferred changed-code gate |

Add new specs here as features stabilize.

---

## Development workflow

| Document | Purpose |
|----------|---------|
| [GIT_WORKFLOW.md](./GIT_WORKFLOW.md) | Conventional Commits, commitlint, semantic PR titles |
| [TESTING.md](./TESTING.md) | Unit tests, fakes, import rules, pytest config |
| [DEPLOYMENT.md](./DEPLOYMENT.md) | Cloud Run, Artifact Registry, OIDC, local `deploy.sh` |

---

## CI/CD (summary)

| Workflow | Trigger | Action |
|----------|---------|--------|
| `ci.yml` | PR, push to `main` | ruff, pytest + coverage |
| `docker.yml` | PR, push to `main` | pytest, Docker build (no push) |
| `conventional-commits.yml` | PR, push to `main` | commitlint + semantic PR title |
| `deploy.yml` | Tag `v*.*.*`, `workflow_dispatch` | Tests, then OIDC deploy to Cloud Run |

**Important:** do not auto-deploy `main` — single production environment.

---

## Key paths in repo

```
api/handlers/          HTTP handlers
core/config.py         Environment configuration
core/queues.py         Queue names and worker paths
domain/services/       Business logic
infrastructure/        Datastore, Twilio, Claude, Cloud Tasks client
tests/fakes/           In-memory test doubles
tests/unit/            Unit tests
deploy.sh              Local build + push + Cloud Run deploy
Dockerfile             gunicorn main:app on port 8080
pyproject.toml         pytest, ruff, coverage settings
```

---

## Related configuration files

- `.commitlintrc.yaml` — commit message rules
- `requirements-dev.txt` — pytest-cov, ruff
- `.gitignore` — excludes secrets, SDK, local config
