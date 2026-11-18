# Launch checklist — WineAI

**Purpose:** Operator go-live verification after a production release.  
**Commercial gate:** [COMMERCIAL-LAUNCH.md](./COMMERCIAL-LAUNCH.md) item **#68**.  
**As-deployed reference:** [operations/PRODUCTION.md](./operations/PRODUCTION.md) · [DEPLOYMENT.md](./DEPLOYMENT.md)

Use this document to **sign** a launch (or a post-deploy verification). It does **not** replace the phased COMMERCIAL-LAUNCH product gates — complete those separately, then run these checks on the live Cloud Run service.

**Sign-off**

| Field | Value |
|-------|--------|
| Release (tag or dispatch run) | |
| Operator | |
| Date (UTC) | |
| Result | pass / fail |

---

## 1. Deploy

- [ ] Production deploy used a git tag `v*.*.*` **or** `workflow_dispatch` on `.github/workflows/deploy.yml` — **not** an auto-deploy from push to `main`.
- [ ] Deploy workflow finished green (tests, image push, Cloud Run traffic shift, Apply Cloud Scheduler jobs).
- [ ] Live service URL resolves for project `wineia-490200`, service `wine-concierge`, region `southamerica-east1` (see PRODUCTION.md).
- [ ] Current Cloud Run revision matches the intended release image.

```bash
gcloud run services describe wine-concierge \
  --region southamerica-east1 --project wineia-490200 \
  --format='value(status.url)'
```

---

## 2. Secrets and runtime env

Confirm Secret Manager → Cloud Run bindings (or equivalent env) for production. Mapping: [operations/SECRET-MANAGER-MIGRATION.md](./operations/SECRET-MANAGER-MIGRATION.md).

**Integrations**

- [ ] Twilio: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_FROM`
- [ ] Anthropic / Claude keys required by `infrastructure/external/claude_client.py`
- [ ] GCP enqueue: `PROJECT_ID`, `QUEUE_REGION`, `SERVICE_URL`

**Auth and product limits** (must be present and understood)

- [ ] `JOB_INTERNAL_SECRET` set on Cloud Run (fail-closed for `/jobs/*` and `/workers/*` if unset) — [DEPLOYMENT.md](./DEPLOYMENT.md#job_internal_secret-jobs-and-workers)
- [ ] `ON_DEMAND_DAILY_LIMIT_ENTRY` / `ON_DEMAND_DAILY_LIMIT_SUPERIOR` reviewed (defaults 2 / 10) — [T060 SDD](./specs/sdd/T060-per-tier-ia-caps-sdd.md)
- [ ] `CLAUDE_DAILY_CALL_BUDGET` reviewed — **`0` or unset = unlimited**; `> 0` enforces a UTC daily Claude call ceiling — [T061 SDD](./specs/sdd/T061-global-claude-budget-stop-sdd.md). **Production recommendation:** start at **`500`** (ops-tunable guess); do not leave `0` in production without an explicit unlimited decision — [DEPLOYMENT.md](./DEPLOYMENT.md#global-claude-daily-call-budget)

Optional webhook abuse tuning (`WEBHOOK_RATE_LIMIT_*`) is documented in DEPLOYMENT.md; confirm defaults are acceptable for launch traffic.

---

## 3. Cloud Scheduler smoke

Jobs are created/updated by CD — [DEPLOYMENT.md](./DEPLOYMENT.md#cloud-scheduler-jobs-created-by-cd), [ADR 0005](./adrs/0005-cloud-scheduler-from-cd.md).

| Job | Schedule (`America/Sao_Paulo`) | Target |
|-----|--------------------------------|--------|
| `wine-send-recommendations` | Thu + Sat 10:00 (`0 10 * * 4,6`) | `POST /jobs/send-recommendations` |
| `wine-send-weekly-education` | Mon 15:00 (`0 15 * * 1`) | `POST /jobs/send-weekly-education` |

- [ ] Both jobs exist in `southamerica-east1` / project `wineia-490200`.
- [ ] Each job sends `X-Job-Internal-Secret` and `Content-Type: application/json`.
- [ ] Job URIs point at the current Cloud Run service URL + paths above.
- [ ] Smoke: describe both jobs (or run a controlled manual invoke with the secret). Do **not** paste the secret into tickets or chat logs.

```bash
gcloud scheduler jobs describe wine-send-recommendations \
  --location=southamerica-east1 --project=wineia-490200
gcloud scheduler jobs describe wine-send-weekly-education \
  --location=southamerica-east1 --project=wineia-490200
```

---

## 4. Twilio webhook signature

- [ ] Twilio WhatsApp webhook URL points at `https://<live-url>/webhook/whatsapp`.
- [ ] Invalid or missing Twilio signature is rejected (auth failure path).
- [ ] Operators know a webhook **200** can precede Cloud Tasks worker delivery (T032); Twilio will not HTTP-retry a successful 200 for that attempt — [PRODUCTION.md](./operations/PRODUCTION.md), [T032 SDD](./specs/sdd/T032-async-webhook-replies-sdd.md).

---

## 5. Cloud Tasks workers

Queues (see `core/queues.py` / DEPLOYMENT.md):

| Queue | Worker path |
|-------|-------------|
| `wine-messages` | `POST /workers/send-message` |
| `wine-campaigns` | `POST /workers/send-campaign` |

- [ ] Both queues exist and target the live service URL.
- [ ] Worker HTTP requests include `X-Job-Internal-Secret` when `JOB_INTERNAL_SECRET` is set on Cloud Run.
- [ ] Unauthenticated calls to `/workers/*` return **401**.
- [ ] Spot-check: inbound WhatsApp product reply enqueues `send_message` and the worker delivers (or inspect task logs on failure).

---

## 6. Health

- [ ] `GET /health` on the live URL returns success (liveness).

```bash
curl -fsS "$(gcloud run services describe wine-concierge \
  --region southamerica-east1 --project wineia-490200 \
  --format='value(status.url)')/health"
```

---

## 7. Entitlements and Claude budget notes

- [ ] Per-tier on-demand IA caps (ENTRY/SUPERIOR) match intended launch values via env or defaults — [on-demand-entitlements-sdd.md](./specs/on-demand-entitlements-sdd.md), [T060](./specs/sdd/T060-per-tier-ia-caps-sdd.md).
- [ ] Global Claude daily call budget policy decided for launch (`0` = unlimited vs a positive ceiling). Suggested production start: **`500`** (ops-tunable guess) — [T061](./specs/sdd/T061-global-claude-budget-stop-sdd.md), [DEPLOYMENT.md](./DEPLOYMENT.md#global-claude-daily-call-budget).
- [ ] Ops know where to watch: Cloud Run logs (job skip reason `claude daily call budget exceeded`) and Anthropic billing — no PagerDuty hook in T061.

---

## 8. Security exposure

Threat model: [threat-model.md](./threat-model.md).

- [ ] `/ia/suggestions` is **not** publicly reachable in production (VPC / ingress / IAP / or equivalent). Document the control used.
- [ ] Job and worker routes remain secret-gated (`JOB_INTERNAL_SECRET`).
- [ ] Customer-facing WhatsApp copy remains Portuguese where product already requires it; no secrets in Datastore customer records.

---

## 9. Payments (deferred)

**T040–T043 are parked.** Do not block go-live on a payment provider integration.

- [ ] Launch uses **manual customer provisioning** (APIs / operator process) until payments work lands — see COMMERCIAL-LAUNCH #55 and [payments-evaluation.md](./payments-evaluation.md) (evaluation only; no provider claimed as decided on `main`).
- [ ] Operators know how to create/activate customers without an automated billing webhook.
- [ ] No production payment webhook is required for this checklist to pass.

---

## 10. Documentation links (read before signing)

Confirm these are current for the release you are signing:

- [ ] [operations/PRODUCTION.md](./operations/PRODUCTION.md) — routes, Scheduler, env notes
- [ ] [operations/WHATSAPP-COMPLIANCE.md](./operations/WHATSAPP-COMPLIANCE.md) — templates / Twilio-WhatsApp policy (CL #16)
- [ ] [operations/DATA-RETENTION.md](./operations/DATA-RETENTION.md) — LGPD retention intent (CL #61)
- [ ] [DEPLOYMENT.md](./DEPLOYMENT.md) — tag deploy, secrets, Scheduler CD
- [ ] [threat-model.md](./threat-model.md) — trust boundaries
- [ ] [specs/sdd/INDEX.md](./specs/sdd/INDEX.md) — SDD status index
- [ ] [COMMERCIAL-LAUNCH.md](./COMMERCIAL-LAUNCH.md) — phased gates
- [ ] [operations/INCIDENT-RESPONSE.md](./operations/INCIDENT-RESPONSE.md) — on-call path

---

## Related

- [ENGINEERING_MANUAL.md](./ENGINEERING_MANUAL.md)
- [ROADMAP-TASKS.md](./ROADMAP-TASKS.md) — T071
- [specs/sdd/T071-launch-checklist-doc-sdd.md](./specs/sdd/T071-launch-checklist-doc-sdd.md)
