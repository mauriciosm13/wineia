# WineAI

**Gastón** on WhatsApp: a short, opinionated sommelier in Portuguese. Asks are answered in-chat; once a week he pushes **one** bottle from *your* catalog — not a wine marketplace, not a generic bot kit.

This repo is the concierge backend (Cloud Run `wine-concierge`, São Paulo).  
[Roadmap](./docs/ROADMAP.md) · [Deploy](./docs/DEPLOYMENT.md) · [Engineering](./docs/ENGINEERING_MANUAL.md)

**Shipped:** inbound chat, 2 free messages/day, text `cancelar` to stop, Claude copy, pre-sale leads + activate, weekly job via Cloud Tasks, CI/CD.  
**Not this product:** checkout, stock, native apps, multi-tenant SaaS.

---

## Who talks to it

| Who | Reality |
|-----|---------|
| Drinker | WhatsApp only. Three bottles, price *range*, no fake “in stock”. |
| You (operator) | Twilio in, Claude out, Datastore in the middle. Catalog is files/API you load, not a web scrape. |
| A shop / club | Same backend, *if* you own the numbers and the catalog. No shop portal yet. |

---

## Conversation

```text
WhatsApp  →  Twilio  →  POST /webhook/whatsapp
                              │
                    find customer by phone
                    "cancelar" → status canceled
                    else cap at 2 messages / day
                              │
                         Gastón (Claude)
                              │
                         Twilio reply
```

Weekly drop: `POST /jobs/send-recommendations` → rotate catalog (skip recent bottles) → one WhatsApp-sized note → bump `last_recommendation_at`.

Pre-sale form hits `POST /customers/pre-sale` (name, email, WhatsApp, preferences). Promoting that lead to an active customer is still a later milestone.

---

## HTTP surface

Plain WSGI (`main:app`). The router matches **path only** — it does not enforce GET vs POST.

| Path | Role |
|------|------|
| `/health` | Liveness |
| `/customers` | Create customer (phone, plan, status) |
| `/customers/pre-sale` | Lead capture |
| `/customers/pre-sale/activate` | Promote lead → active customer |
| `/webhook/whatsapp` | Twilio inbound (signature required) |
| `/ia/suggestions` | Gastón over HTTP (same voice, no WhatsApp) |
| `/recommendation-contents` | Add a bottle to the weekly catalog |
| `/jobs/send-recommendations` | Fan-out weekly recommendation (Cloud Tasks) |
| `/workers/send-message` | Outbound worker |

---

## Gaps (do not skip)

- Inbound WhatsApp replies are still **synchronous** in the webhook (only the weekly job enqueues Cloud Tasks).
- `/workers/send-campaign` and Scheduler-from-CD are not done.
- Weekly enqueue needs `SERVICE_URL` and `PROJECT_ID` on Cloud Run.

---

## Stack

Python 3.11 · gunicorn · GCP (Cloud Run, Datastore, Artifact Registry) · Twilio · Anthropic Claude.

Layers: `api/` → `domain/` → `infrastructure/`, plus `core/`. **Domain never imports infrastructure.**

[AGENTS.md](./AGENTS.md) for contributors.

---

## Run locally

Python 3.11+. Copy [`config.example.json`](./config.example.json) → `config.json` (gitignored): Anthropic + Twilio fields.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
ruff check api core domain infrastructure tests
pytest --cov    # domain + core; fail_under 95
```

Fakes only — no Datastore emulator. `tests/conftest.py` stubs `datastore.Client`.  
[docs/TESTING.md](./docs/TESTING.md)

Live WhatsApp: tunnel to `/webhook/whatsapp` and point Twilio at it. Also set `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_FROM` on Cloud Run.

---

## Ship

CI on every PR/`main` (ruff, pytest, coverage, Docker build without push).  
**Production does not deploy from `main`.** Tag `v*.*.*` or run Deploy by hand (OIDC → Artifact Registry → Cloud Run).

```bash
./deploy.sh    # local gcloud + Docker
```

[docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md)

---

## Next (product, not process)

Twilio signatures · Cloud Tasks for send · daily counter reset · pre-sale → customer · preferences in the prompt.

Full checklist: [docs/ROADMAP.md](./docs/ROADMAP.md).
