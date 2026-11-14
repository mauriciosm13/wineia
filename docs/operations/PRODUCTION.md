# Production — WineAI (as deployed)

**Update this file in the same PR as any behavior change.**

## GCP

| Item | Value |
|------|--------|
| Project | `wineia-490200` |
| Cloud Run service | `wine-concierge` |
| Region | `southamerica-east1` |
| Image | `southamerica-east1-docker.pkg.dev/wineia-490200/wine-concierge/wine-concierge` |
| Entry | `gunicorn -b 0.0.0.0:8080 main:app` |

Live URL:

```bash
gcloud run services describe wine-concierge \
  --region southamerica-east1 --project wineia-490200 \
  --format='value(status.url)'
```

## HTTP routes (path match in `api/routes.py`)

| Path | Notes |
|------|--------|
| `/health` | Liveness |
| `/customers`, `/customers/{phone}` | CRUD-style customer API — JSON includes `plan_tier` (`ENTRY`\|`SUPERIOR`, default `ENTRY`), `weekly_education_opt_in` (bool, default `false`), scheduled cadence fields `recommendation_window_started_at`, `recommendation_send_count_7d`, `last_recommendation_at` (see [entry-recommendation-cadence-sdd.md](../specs/entry-recommendation-cadence-sdd.md)), legacy `plan` string — [customer-plan-tier.md](../specs/customer-plan-tier.md) |
| `/customers/pre-sale` | Pre-sale registration |
| `/webhook/whatsapp` | Twilio inbound — on-demand IA gated by `plan_tier` daily cap (`messages_sent_today`, `daily_reset`) — [on-demand-entitlements-sdd.md](../specs/on-demand-entitlements-sdd.md); signature validated; IP + phone rate limits — [webhook-rate-limit.md](../specs/webhook-rate-limit.md) |
| `/jobs/send-recommendations` | Scheduled recommendation job (ENTRY/SUPERIOR): max **2** sends per rolling **168h**; **one** Claude copy per run fan-out to eligibles — requires `X-Job-Internal-Secret` — [recommendation-broadcast-slot.md](../specs/recommendation-broadcast-slot.md), [entry-recommendation-cadence-sdd.md](../specs/entry-recommendation-cadence-sdd.md) |
| `/jobs/send-weekly-education` | Weekly didactic message for `weekly_education_opt_in` cohort — rolling 7-day cadence — [weekly-education-job.md](../specs/weekly-education-job.md) |
| `/workers/send-message` | Cloud Tasks worker — requires `X-Job-Internal-Secret` |
| `/workers/send-campaign` | Cloud Tasks campaign worker — requires `X-Job-Internal-Secret` |
| `/ia/suggestions` | IA suggestion generation |
| `/recommendation-contents` | Catalog content create |

Router logs method + path via `core.logging.log_request`. Unknown paths → 404 plain text.

## Cloud Scheduler jobs

Created or updated by the deploy workflow on every production deploy — [DEPLOYMENT.md](../DEPLOYMENT.md#cloud-scheduler-jobs-created-by-cd), [ADR 0005](../adrs/0005-cloud-scheduler-from-cd.md).

| Job | Schedule (`America/Sao_Paulo`) | Target |
|-----|--------------------------------|--------|
| `wine-send-recommendations` | Thursday and Saturday 10:00 (`0 10 * * 4,6`) | `POST /jobs/send-recommendations` |
| `wine-send-weekly-education` | Monday 15:00 (`0 15 * * 1`) | `POST /jobs/send-weekly-education` |

## Integrations

| System | Module |
|--------|--------|
| WhatsApp | Twilio — `infrastructure/external/twilio_whatsapp_client.py` |
| LLM | Claude — `infrastructure/external/claude_client.py` |
| DB | Datastore kinds: Customer, pre-sale, recommendation content/history |
| Async | `infrastructure/queue/cloud_tasks_client.py`, queues in `core/queues.py` |

## Deploy

- **CI/CD:** tag `v*.*.*` or `workflow_dispatch` — [.github/workflows/deploy.yml](../.github/workflows/deploy.yml)
- **Local:** [DEPLOYMENT.md](../DEPLOYMENT.md), `./deploy.sh`
- **Not auto-deploy on push to `main`**

## Config

Runtime config via env / `core/config.py` / `config.example.json` — never commit secrets.

**Production secrets:** Google Secret Manager → Cloud Run env refs — [SECRET-MANAGER-MIGRATION.md](./SECRET-MANAGER-MIGRATION.md).

**Job/worker auth:** set `JOB_INTERNAL_SECRET` on Cloud Run. Callers (Scheduler, Cloud Tasks, manual curl) must send header `X-Job-Internal-Secret` with the same value. See [DEPLOYMENT.md](../DEPLOYMENT.md#job_internal_secret-jobs-and-workers).

**Webhook rate limits:** optional env tuning — `WEBHOOK_RATE_LIMIT_IP_*` and `WEBHOOK_RATE_LIMIT_PHONE_*` (defaults in [DEPLOYMENT.md](../DEPLOYMENT.md#whatsapp-webhook-rate-limits)).

## Security

Threat model (webhook abuse, LLM injection, job auth, secrets): [threat-model.md](../threat-model.md).

## Related

- [INCIDENT-RESPONSE.md](./INCIDENT-RESPONSE.md)
- [OBSERVABILITY.md](./OBSERVABILITY.md)
- [DEPLOYMENT.md](../DEPLOYMENT.md)
