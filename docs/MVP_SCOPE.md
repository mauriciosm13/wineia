# MVP Scope

This document defines the **Minimum Viable Product** for WineAI: what must be delivered for a first production release versus what is explicitly deferred.

---

## In scope (MVP)

The MVP is the **delivered subset of milestones M0 through M4**, plus **later wiring for M5** (campaign queues and scheduler) without blocking initial launch.

### M0 — Foundation (required)

All delivered M0 items except optional/deferred work:

- Clean Architecture layout and deployment to Cloud Run
- CI (pytest, ruff, coverage), Docker build CI, conventional commits, CD via OIDC
- Unit tests with pure mocks and coverage gate bootstrap
- Documentation process (RFC, ADR, SPEC templates; engineering manual)

**Deferred within M0 for MVP:** mypy, structured logging (nice-to-have before scale, not MVP blocker).

**Should complete before public launch:** repo hygiene (no tracked secrets, SDK artifacts, or accidental keys in the workspace).

### M1 — Customers (partial OK for MVP)

- **In:** `POST /customers`, Datastore persistence, plan/status
- **Later (post-MVP):** HTTP list/get/update, automated daily message counter reset

### M2 — WhatsApp (core path)

- **In:** Twilio webhook, daily 2-message limit, cancel via `"cancelar"`
- **Later (post-MVP):** Twilio signature validation, async queue for replies ( overlaps M5 wiring)

### M3 — Recommendations

- **In:** Claude sommelier, recommendation contents, selector rotation, send-recommendations job, IA suggestions endpoint
- **Later:** preferences injected into campaign/recommendation prompts

### M4 — Pre-sale

- **In:** `POST /customers/pre-sale` with name, email, whatsapp, preferences
- **Later:** convert pre-sale → active customer (can be manual ops initially)

### M5 — Campaigns (wiring later)

MVP may ship with **direct worker calls** where queues are not yet wired. Full campaign automation (Cloud Tasks client in use, `/workers/send-campaign`, Scheduler in CD) is **post-MVP** but planned immediately after launch stabilization.

---

## Out of scope (not MVP)

The following are **explicitly excluded** from the MVP definition:

| Area | Reason |
|------|--------|
| **M6 Analytics** | No event pipeline or dashboards in MVP |
| **M7 Preference learning** (beyond pre-sale capture) | Dynamic profiles and personalization come after core messaging works |
| **Datastore emulator** | Unit tests use pure mocks/fakes; no local emulator requirement |
| **mypy** | Deferred type-checking gate |
| **Second Cloud Run environment** | Single production environment only; no staging slot |
| **Kubernetes** | Cloud Run is the deployment target |

---

## MVP success definition

WineAI MVP is achieved when:

1. A user can register via pre-sale or customer APIs.
2. WhatsApp webhook handles inbound messages and respects daily limits and cancel.
3. Scheduled or manual job can send AI-generated wine recommendations to active customers.
4. Service runs on Cloud Run in `wineia-490200` with tag-based or manual deploy.
5. CI quality gate passes on `main` PRs.

For milestone tracking and checkboxes, see [ROADMAP.md](./ROADMAP.md).
