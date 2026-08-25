# WineAI Product Roadmap

This roadmap tracks product milestones for WineAI — an intelligent pocket sommelier delivered over WhatsApp. Each milestone lists deliverables, success criteria, and open work. Status uses checkboxes: `[x]` delivered, `[ ]` not yet delivered, `[~]` partial.

**Deployment model:** single Cloud Run environment (production). Releases deploy via git tags `v*.*.*` and `workflow_dispatch`, not automatically on every push to `main`.

---

## Engineering Rule

Every milestone item that introduces or changes behavior must pass the quality gate before it is considered complete:

| Artifact | When |
|----------|------|
| **RFC** (lite is OK) | Substantial design or process change |
| **SPEC** | New or changed runtime behavior |
| **ADR** | New dependency, integration, or architectural decision |
| **Tests** | Domain logic and critical handlers |
| **Docs** | User-facing or operator-facing updates |

No feature is **complete** until tests pass, lint passes, coverage gate passes (where applicable), and relevant docs are merged.

See [ENGINEERING_MANUAL.md](./ENGINEERING_MANUAL.md) for templates and process links.

---

## M0 — Foundation

Core platform, CI/CD, and documentation process.

| Item | Status |
|------|--------|
| Clean Architecture (`api/`, `domain/`, `infrastructure/`, `core/`) | [x] |
| Dockerfile + gunicorn WSGI (`main:app`) | [x] |
| Local `deploy.sh` to Cloud Run (`wine-concierge`, `southamerica-east1`, Artifact Registry) | [x] |
| `agent.md` architecture notes | [x] |
| RFC / ADR / SPEC templates | [x] |
| GitHub Actions CI (pytest, ruff, coverage) | [x] |
| GitHub Actions Docker image build (no push) | [x] |
| Conventional Commits CI | [x] |
| GitHub Actions CD (OIDC → Artifact Registry → Cloud Run) | [x] |
| Unit tests with pure mocks | [x] |
| Coverage gate bootstrap | [x] |
| Repo hygiene (remove accidental SDK/keys from workspace; tracked ignore rules) | [ ] |
| Structured logging (replace `print` in `api/routes.py`) | [x] |
| mypy (deferred) | [ ] |

**Success criteria**

- PRs to `main` run pytest, ruff, and coverage; Docker image builds in CI without push.
- Production deploy requires a version tag or manual workflow dispatch; OIDC auth, no JSON keys in GitHub.
- New contributors can find architecture, testing, deployment, and git conventions in `docs/`.

**References:** [RFC 0001](./rfcs/0001-engineering-foundation.md), [DEPLOYMENT.md](./DEPLOYMENT.md), [TESTING.md](./TESTING.md)

---

## M1 — Customers

Customer lifecycle in Datastore.

| Item | Status |
|------|--------|
| `POST /customers` — create customer with plan/status | [x] |
| Datastore persistence | [x] |
| HTTP list / get / update | [ ] |
| Daily message counter reset | [ ] |

**Success criteria**

- Active customers can be created via API with validated plan and status.
- List, get, and update endpoints return consistent JSON and enforce domain rules.
- A scheduled or job-triggered process resets `messages_sent_today` at day boundary.

---

## M2 — WhatsApp

Inbound/outbound messaging via Twilio.

| Item | Status |
|------|--------|
| `POST /webhook/whatsapp` (Twilio) | [x] |
| Daily limit — 2 messages per customer | [x] |
| Cancel via `"cancelar"` | [x] |
| Twilio signature validation | [x] |
| Async queue for replies | [ ] |

**Success criteria**

- Webhook accepts Twilio payloads and routes to domain messaging logic.
- Customers exceeding the daily cap are not sent additional proactive messages.
- `"cancelar"` sets customer status to canceled.
- Requests without valid Twilio signatures are rejected.
- Outbound replies are enqueued (Cloud Tasks) rather than sent synchronously in the webhook handler.

---

## M3 — Recommendations

AI sommelier and recommendation content pipeline.

| Item | Status |
|------|--------|
| Claude sommelier (Gastón) | [x] |
| Recommendation contents CRUD — `POST /recommendation-contents` | [x] |
| Selector rotation | [x] |
| `POST /jobs/send-recommendations` | [x] |
| `POST /ia/suggestions` | [x] |
| Preferences in campaign prompt | [x] |

**Success criteria**

- Job endpoint selects wine content, generates copy via IA service, and sends to eligible active customers.
- Recommendation content can be created and rotated fairly across the catalog.
- Customer preferences (when available) are included in recommendation/campaign prompts.

---

## M4 — Pre-sale

Capture leads before full onboarding.

| Item | Status |
|------|--------|
| `POST /customers/pre-sale` (name, email, whatsapp, preferences) | [x] |
| Convert pre-sale → active customer | [x] |

**Success criteria**

- Pre-sale records persist with validated contact fields and non-empty preference lists.
- An operator or automated flow can promote a pre-sale record to an active customer without duplicate keys.

---

## M5 — Campaigns

Scheduled and queued outbound campaigns. **Treat as partial.**

| Item | Status |
|------|--------|
| Job endpoint | [x] |
| Worker `/workers/send-message` | [x] |
| Queue config in `core/queues.py` | [x] |
| Cloud Tasks client wired (`send_recommendations` enqueues `wine-messages`) | [x] |
| `/workers/send-campaign` | [ ] |
| Scheduler created by CD | [ ] |

**Success criteria**

- Campaign jobs enqueue per-recipient tasks; workers send via WhatsApp adapter.
- Cloud Tasks queues (`wine-messages`, `wine-campaigns`) are created and IAM-scoped.
- Cloud Scheduler jobs (e.g. daily recommendations) are provisioned as part of deployment automation.

---

## M6 — Analytics

| Item | Status |
|------|--------|
| Event capture | [ ] |
| Dashboards / exports | [ ] |
| Recommendation and campaign metrics | [ ] |

**Success criteria**

- Key funnel events (pre-sale, activation, message sent, recommendation opened) are queryable for product decisions.

---

## M7 — Preference learning

| Item | Status |
|------|--------|
| Capture on pre-sale | [x] |
| Dynamic profile | [ ] |
| Selector / IA personalization | [ ] |

**Success criteria**

- Preferences collected at pre-sale feed a durable profile used by selector and IA prompts.
- Recommendations measurably reflect stated preferences over time.

---

## MVP scope

See [MVP_SCOPE.md](./MVP_SCOPE.md) for what is in scope for the first production-ready release versus later milestones.
