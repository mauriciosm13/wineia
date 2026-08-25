# AGENTS.md — WineAI Contributor Guide

Guidance for AI agents and developers working in this repository. Follow these rules when proposing or implementing changes.

**Start here:** [docs/ENGINEERING_MANUAL.md](docs/ENGINEERING_MANUAL.md) · [docs/ROADMAP.md](docs/ROADMAP.md)

---

## Project overview

WineAI is a **Python 3.11+ backend on Google Cloud Platform** that acts as an intelligent pocket sommelier over **WhatsApp**. It handles customer lifecycle, AI wine recommendations, inbound/outbound messaging, and (in progress) scheduled campaigns via queues.

The codebase follows **Clean Architecture** with strict layer boundaries.

---

## Directory layout

```
api/              HTTP routing, handlers, status codes — no business logic
core/             Config, logging, queue definitions — framework-independent
domain/           Models, services, repository interfaces — business rules
infrastructure/   Datastore, Twilio, Claude, Cloud Tasks — external integrations
tests/            Unit tests and fakes
docs/             Roadmap, specs, ADRs, engineering manual
```

---

## Dependency rules

Dependencies flow **inward**:

```
api → domain → infrastructure (via interfaces implemented in infrastructure)
core is shared; domain must not import infrastructure
```

| Rule | Detail |
|------|--------|
| `domain` must never import `infrastructure` | Use repository interfaces; wire implementations in handlers or composition root |
| `api` must not contain business logic | Handlers parse HTTP and call domain services |
| External services live in `infrastructure/` | Datastore, Cloud Tasks, WhatsApp, Claude |

---

## Coding style

- **PEP 8** strictly
- **Prefer functions** over instance-heavy classes; use stateless services and dependency injection
- Descriptive names, small functions, no global mutable state
- See existing handlers and `domain/services/` for patterns

---

## Google Cloud integration

Target platform:

| Service | Use |
|---------|-----|
| **Cloud Run** | HTTP API and workers (`wine-concierge`, `southamerica-east1`) |
| **Cloud Tasks** | Async message and campaign delivery (client exists; wiring in progress) |
| **Cloud Scheduler** | Trigger job endpoints (not yet in CD) |
| **Datastore** | Customers, pre-sale, recommendation content |

Isolate all GCP SDK usage under `infrastructure/`.

---

## Queue-based messaging

Outbound sends should be **queue-based**, not long synchronous work in webhooks:

```
Scheduler → Job endpoint → Cloud Tasks → Worker endpoint → WhatsApp (Twilio)
```

Queue definitions: `core/queues.py`  
Client: `infrastructure/queue/cloud_tasks_client.py`

---

## AI integration

Claude and other LLM clients belong in `infrastructure/external/`. Domain services (e.g. `ia_service`, `recommendation_service`) orchestrate prompts; they must not import SDK clients directly from handlers without going through domain boundaries.

---

## API surface (current)

| Method | Path |
|--------|------|
| GET | `/health` |
| POST | `/customers` |
| POST | `/customers/pre-sale` |
| POST | `/webhook/whatsapp` |
| POST | `/jobs/send-recommendations` |
| POST | `/workers/send-message` |
| POST | `/ia/suggestions` |
| POST | `/recommendation-contents` |

Handlers delegate to `domain/services`.

---

## Testing expectations

- Unit tests with **pure mocks/fakes** — no Datastore emulator in CI
- Do **not** import `api.handlers` that construct Datastore at module import time
- `testpaths = tests`; skip `google-cloud-sdk` in collection
- See [docs/TESTING.md](docs/TESTING.md)

---

## Engineering process

Before marking work complete:

1. **RFC** (lite OK) for substantial design
2. **SPEC** for new behavior
3. **ADR** for new dependencies or architecture decisions
4. **Tests** for domain logic
5. **Docs** updates

Quality gate: pytest, ruff, coverage — see [docs/specs/coverage-gate.md](docs/specs/coverage-gate.md).

---

## Deployment constraints

- **Single production** Cloud Run environment
- Deploy via **git tag `v*.*.*`** or **workflow_dispatch** — not auto on `main`
- OIDC to GCP — no JSON keys in GitHub
- See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

---

## Commits and PRs

Conventional Commits: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.  
See [docs/GIT_WORKFLOW.md](docs/GIT_WORKFLOW.md) and `.commitlintrc.yaml`.

---

## Do not

- Add business logic to `api/routes.py` or handlers beyond HTTP concerns
- Import infrastructure from `domain/`
- Commit secrets, `config.json`, or `google-cloud-sdk`
- Auto-deploy from `main` without explicit release process
- Delete or rewrite product code when asked for documentation-only tasks

---

## Human-oriented architecture notes

Additional detail: [agent.md](agent.md)
