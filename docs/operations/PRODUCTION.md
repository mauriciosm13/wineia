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
| `/customers`, `/customers/{phone}` | CRUD-style customer API |
| `/customers/pre-sale` | Pre-sale registration |
| `/webhook/whatsapp` | Twilio inbound (signature validated) |
| `/jobs/send-recommendations` | Recommendation batch job — requires `X-Job-Internal-Secret` |
| `/workers/send-message` | Cloud Tasks worker — requires `X-Job-Internal-Secret` |
| `/ia/suggestions` | IA suggestion generation |
| `/recommendation-contents` | Catalog content create |

Router logs method + path via `core.logging.log_request`. Unknown paths → 404 plain text.

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

**Job/worker auth:** set `JOB_INTERNAL_SECRET` on Cloud Run. Callers (Scheduler, Cloud Tasks, manual curl) must send header `X-Job-Internal-Secret` with the same value. See [DEPLOYMENT.md](../DEPLOYMENT.md#job_internal_secret-jobs-and-workers).

## Related

- [INCIDENT-RESPONSE.md](./INCIDENT-RESPONSE.md)
- [OBSERVABILITY.md](./OBSERVABILITY.md)
- [DEPLOYMENT.md](../DEPLOYMENT.md)
