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

## HTTP routes (path match in `api/routes.py` + customer handler)

| Path | Notes |
|------|--------|
| `/health` | Liveness |
| `/customers`, `/customers/{phone}` | CRUD-style customer API (`GET`/`POST` list-create; `GET`/`PATCH` by phone) — JSON includes `plan_tier` (`ENTRY`\|`SUPERIOR`, default `ENTRY`), `weekly_education_opt_in` (bool, default `false`), scheduled cadence fields `recommendation_window_started_at`, `recommendation_send_count_7d`, `last_recommendation_at` (see [entry-recommendation-cadence-sdd.md](../specs/entry-recommendation-cadence-sdd.md)), legacy `plan` string — [customer-plan-tier.md](../specs/customer-plan-tier.md). Requires `X-Job-Internal-Secret` ([T072](../specs/sdd/T072-operator-api-auth-sdd.md)). |
| `/customers/{phone}/export` | LGPD export JSON (customer PII + optional pre-sale) — requires `X-Job-Internal-Secret` — [LGPD-EXPORT-DELETE.md](./LGPD-EXPORT-DELETE.md), [T051 SDD](../specs/sdd/T051-export-delete-tooling-sdd.md) |
| `/customers/{phone}/erase` | LGPD anonymize (POST): REDACTED name/preferences, status `canceled`, delete linked pre-sale; does not hard-delete recommendation/financial history — requires `X-Job-Internal-Secret` — [LGPD-EXPORT-DELETE.md](./LGPD-EXPORT-DELETE.md) |
| `/customers/pre-sale` | Pre-sale registration (`POST`) — stamps privacy/terms consent (`privacy_terms_version`, `privacy_terms_accepted_at`) and returns Portuguese `privacy_terms_notice` with `PRIVACY_POLICY_URL` / `TERMS_OF_SERVICE_URL` (placeholders if unset) — requires `X-Job-Internal-Secret` — [T050 SDD](../specs/sdd/T050-privacy-terms-opt-in-sdd.md) |
| `/customers/pre-sale/activate` | Pre-sale activation (`POST`) — promotes pre-sale to customer; returns/copies privacy-terms notice and consent metadata — requires `X-Job-Internal-Secret` — [T050 SDD](../specs/sdd/T050-privacy-terms-opt-in-sdd.md) |
| `/webhook/whatsapp` | Twilio inbound — Grok (text/vision) stays in-request; product outbound (IA reply + limit warning) enqueued to Cloud Tasks `send_message` → `/workers/send-message` — [T032 SDD](../specs/sdd/T032-async-webhook-replies-sdd.md); on-demand IA gated by `plan_tier` daily cap (`messages_sent_today`, `daily_reset`; defaults ENTRY=2 / SUPERIOR=10, ops-tunable via `ON_DEMAND_DAILY_LIMIT_ENTRY` / `ON_DEMAND_DAILY_LIMIT_SUPERIOR`) — [on-demand-entitlements-sdd.md](../specs/on-demand-entitlements-sdd.md), [T060 SDD](../specs/sdd/T060-per-tier-ia-caps-sdd.md); inbound media (image/audio) — see **Inbound WhatsApp media** below; signature validated; IP + phone rate limits — [webhook-rate-limit.md](../specs/webhook-rate-limit.md). A webhook **200** can precede worker delivery; Twilio does not HTTP-retry a successful 200 for that attempt. |
| `/jobs/send-recommendations` | Scheduled recommendation job (ENTRY/SUPERIOR): max **2** sends per rolling **168h**; **one** Grok copy per run fan-out to eligibles — requires `X-Job-Internal-Secret` — [recommendation-broadcast-slot.md](../specs/recommendation-broadcast-slot.md), [entry-recommendation-cadence-sdd.md](../specs/entry-recommendation-cadence-sdd.md) |
| `/jobs/send-weekly-education` | Weekly didactic message for `weekly_education_opt_in` cohort — rolling 7-day cadence — requires `X-Job-Internal-Secret` — [weekly-education-job.md](../specs/weekly-education-job.md) |
| `/workers/send-message` | Cloud Tasks worker — requires `X-Job-Internal-Secret` |
| `/workers/send-campaign` | Cloud Tasks campaign worker — requires `X-Job-Internal-Secret` |
| `/ia/suggestions` | IA suggestion generation — requires `X-Job-Internal-Secret` ([T072](../specs/sdd/T072-operator-api-auth-sdd.md)) |
| `/recommendation-contents` | Catalog content create — requires `X-Job-Internal-Secret` ([T072](../specs/sdd/T072-operator-api-auth-sdd.md)) |

Router logs method + path via `core.logging.log_request`. Unknown paths → 404 plain text.

## Cloud Scheduler jobs

Created or updated by the deploy workflow on every production deploy — [DEPLOYMENT.md](../DEPLOYMENT.md#cloud-scheduler-jobs-created-by-cd), [ADR 0005](../adrs/0005-cloud-scheduler-from-cd.md).

| Job | Schedule (`America/Sao_Paulo`) | Target |
|-----|--------------------------------|--------|
| `wine-send-recommendations` | Thursday and Saturday 10:00 (`0 10 * * 4,6`) | `POST /jobs/send-recommendations` |
| `wine-send-weekly-education` | Monday 15:00 (`0 15 * * 1`) | `POST /jobs/send-weekly-education` |

## Inbound WhatsApp media (T074–T079)

Twilio may deliver **image** or **audio** on `POST /webhook/whatsapp` (`NumMedia`, `MediaUrl0`, `MediaContentType0`), including media-only messages with an empty `Body`.

| Topic | Production behavior |
|-------|---------------------|
| Download | Authenticated `GET MediaUrl0` via `twilio_media_client.py` (HTTP Basic Auth; follow redirect). MIME allowlist + size caps (images ≤5 MiB, audio ≤16 MiB) — [T076](../specs/sdd/T076-twilio-media-download-sdd.md). |
| Image | Grok vision (+ optional `Body` caption) — [T078](../specs/sdd/T078-inbound-image-vision-sdd.md) / [T082](../specs/sdd/T082-grok-chat-vision-client-sdd.md); client `grok_client.py`. |
| Audio | Grok Voice Transcribe STT → existing text IA path — [T077](../specs/sdd/T077-inbound-audio-stt-sdd.md) / [T083](../specs/sdd/T083-grok-stt-replace-whisper-sdd.md); client `grok_stt_client.py` (`XAI_API_KEY`; [ADR 0007](../adrs/0007-xai-grok-ia-stack.md)). |
| Fail closed | Unsupported MIME, download failure, STT/vision failure → short Portuguese reply; no silent ignore when the customer sent media. |
| Ephemeral bytes | Raw media is held only for the request turn (download → STT/vision). **No** long-term Datastore/blob storage of media bytes — [DATA-RETENTION.md](./DATA-RETENTION.md). |
| Entitlements / budget | A successful media turn counts as one on-demand IA turn (same daily cap as text). Global daily IA call budget (T061 / `CLAUDE_DAILY_CALL_BUDGET`) still applies to vision/text generations after STT. Fail-closed media replies do **not** increment the daily counter. |
| Text-only | Unchanged when `NumMedia=0`. |

Ops/tests slice: [T079 SDD](../specs/sdd/T079-inbound-media-ops-tests-sdd.md). Residual large-media DoS notes: [threat-model.md](../threat-model.md) §4.1.

## Integrations

| System | Module |
|--------|--------|
| WhatsApp | Twilio — `infrastructure/external/twilio_whatsapp_client.py`; media download — `twilio_media_client.py` |
| LLM | **Grok** (text + vision primary) — `infrastructure/external/grok_client.py` (`XAI_API_KEY`; ADR 0007 / T082); Claude client kept for rollback |
| STT | **Grok Voice Transcribe** — `infrastructure/external/grok_stt_client.py` (`XAI_API_KEY`; ADR 0007 / T083) |
| DB | Datastore kinds: `Customer`, `PreSaleCustomer`, `RecommendationContent`, `RecommendationHistory`, `ClaudeDailyBudget` |
| Async | `infrastructure/queue/cloud_tasks_client.py`; queues in `core/queues.py`: `wine-messages` → `/workers/send-message`, `wine-campaigns` → `/workers/send-campaign` |

## Deploy

- **CI/CD:** tag `v*.*.*` or `workflow_dispatch` — [.github/workflows/deploy.yml](../.github/workflows/deploy.yml)
- **Local:** [DEPLOYMENT.md](../DEPLOYMENT.md), `./deploy.sh`
- **Not auto-deploy on push to `main`**

## Config

Runtime config via env / `core/config.py` / `config.example.json` — never commit secrets.

**Production secrets:** Google Secret Manager → Cloud Run env refs — [SECRET-MANAGER-MIGRATION.md](./SECRET-MANAGER-MIGRATION.md).

**Job/worker/operator auth:** set `JOB_INTERNAL_SECRET` on Cloud Run. Callers (Scheduler, Cloud Tasks, operators, manual curl) must send header `X-Job-Internal-Secret` with the same value for `/jobs/*`, `/workers/*`, `/customers*`, `/ia/suggestions`, and `/recommendation-contents`. Fail closed if unset. See [DEPLOYMENT.md](../DEPLOYMENT.md#job_internal_secret-jobs-workers-and-operator-apis).

**Webhook rate limits:** optional env tuning — `WEBHOOK_RATE_LIMIT_IP_*` and `WEBHOOK_RATE_LIMIT_PHONE_*` (defaults in [DEPLOYMENT.md](../DEPLOYMENT.md#whatsapp-webhook-rate-limits)).

**Global Claude daily call budget:** optional env `CLAUDE_DAILY_CALL_BUDGET` (default `0` = unlimited). When set `> 0`, the IA choke point stops new Claude generations for the UTC day after the call count is reached; jobs log `claude daily call budget exceeded` and skip fan-out; webhook customers get a short Portuguese unavailable message. No PagerDuty hook in T061 — ops watch Cloud Run logs and Anthropic billing. Spec: [T061 SDD](../specs/sdd/T061-global-claude-budget-stop-sdd.md). **Production recommendation:** start at **`500`** (ops-tunable guess); `0`/unset remains unlimited — [DEPLOYMENT.md](../DEPLOYMENT.md#global-claude-daily-call-budget).

**Privacy / terms opt-in:** optional env `PRIVACY_POLICY_URL` and `TERMS_OF_SERVICE_URL` (defaults `https://example.com/privacy` / `https://example.com/terms`). Pre-sale create and activation return notice copy with those links and persist consent metadata; unset URLs do not block registration. Spec: [T050 SDD](../specs/sdd/T050-privacy-terms-opt-in-sdd.md).

## Security

Threat model (webhook abuse, LLM injection, job auth, secrets): [threat-model.md](../threat-model.md).

## Related

- [INCIDENT-RESPONSE.md](./INCIDENT-RESPONSE.md)
- [OBSERVABILITY.md](./OBSERVABILITY.md)
- [LGPD-EXPORT-DELETE.md](./LGPD-EXPORT-DELETE.md)
- [WHATSAPP-COMPLIANCE.md](./WHATSAPP-COMPLIANCE.md)
- [DATA-RETENTION.md](./DATA-RETENTION.md)
- [DEPLOYMENT.md](../DEPLOYMENT.md)
