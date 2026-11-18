# Deployment

WineAI runs as a **single Cloud Run service** in production. There is **no staging Cloud Run environment** in this repository — deploy carefully using tags or manual workflow dispatch.

---

## Environment summary

| Setting | Value |
|---------|-------|
| GCP project | `wineia-490200` |
| Cloud Run service | `wine-concierge` |
| Region | `southamerica-east1` |
| Artifact Registry | `southamerica-east1-docker.pkg.dev/wineia-490200/wine-concierge/wine-concierge` |
| WSGI entrypoint | `gunicorn -b 0.0.0.0:8080 main:app` |

Queues (configured in `core/queues.py`, provisioned separately):

- `wine-messages` → worker `/workers/send-message`
- `wine-campaigns` → worker `/workers/send-campaign`

---

## Deploy paths

### 1. CI/CD (recommended for production)

**Workflow:** `.github/workflows/deploy.yml`

**Triggers:**

- Git tag matching `v*.*.*` (e.g. `v0.1.0`)
- **`workflow_dispatch`** — manual run from GitHub Actions UI

**Not triggered:** push to `main` alone. Because the only environment is prod, merges to `main` do not deploy automatically.

**Steps:**

1. Run ruff + pytest + coverage (same as CI)
2. Authenticate to GCP via **OIDC / Workload Identity Federation**
3. Build and push Docker image to Artifact Registry
4. `gcloud run deploy` with `--no-traffic`, then shift traffic to latest revision
5. Create or update the Cloud Scheduler jobs — see [Cloud Scheduler jobs (created by CD)](#cloud-scheduler-jobs-created-by-cd)

**GitHub configuration:**

| Name | Kind | Purpose |
|------|------|---------|
| `WIF_PROVIDER` | Repository variable | Full WIF provider resource name |
| `WIF_SERVICE_ACCOUNT` | Repository variable | Deploy service account email |
| `production` | GitHub Environment | Optional approval gate before deploy job |

See [ADR 0001](./adrs/0001-github-oidc-gcp.md).

**Release example:**

```bash
git tag v0.1.0
git push origin v0.1.0
```

### 2. Local operator deploy

**Script:** `./deploy.sh`

Uses local `gcloud` and Docker credentials:

1. Configure Docker for Artifact Registry
2. Build `linux/amd64` image tagged with git SHA and `latest`
3. Push to Artifact Registry
4. Deploy Cloud Run and shift traffic to latest

Requires:

- `gcloud` CLI authenticated to `wineia-490200`
- Docker with BuildKit

---

## GCP setup — Workload Identity Federation

One-time setup (high level; adjust names to your org):

1. **Create Workload Identity Pool** and **OIDC provider** for GitHub Actions (`token.actions.githubusercontent.com`).
2. **Attribute mapping** — map `assertion.sub` to Google subject; restrict to this repository (and optionally environment/ref).
3. **Service account** for deploy (e.g. `github-deploy@wineia-490200.iam.gserviceaccount.com`).
4. **Bind** pool principal to service account (`roles/iam.workloadIdentityUser`).
5. Set GitHub vars `WIF_PROVIDER` and `WIF_SERVICE_ACCOUNT`.

Official guide: [Workload Identity Federation with deployment pipelines](https://cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines)

---

## GCP setup — Artifact Registry

```bash
gcloud artifacts repositories create wine-concierge \
  --repository-format=docker \
  --location=southamerica-east1 \
  --project=wineia-490200
```

Deploy service account needs **`roles/artifactregistry.writer`** on the repository (or project).

---

## GCP setup — Cloud Run IAM

Deploy service account minimum roles:

| Role | Purpose |
|------|---------|
| `roles/run.admin` | Create/update Cloud Run services |
| `roles/artifactregistry.writer` | Push images |
| `roles/iam.serviceAccountUser` | Deploy revisions that run as the runtime SA |

Runtime service account (Cloud Run execution SA) needs access to Datastore, Secret Manager (if used), and any APIs invoked at runtime — configure separately from deploy SA.

---

## Cloud Tasks and Scheduler (M5 — partial)

- `infrastructure/queue/cloud_tasks_client.py` exists but is **not wired**; add `google-cloud-tasks` to `requirements.txt` when enqueue is used in production paths.
- Cloud Scheduler jobs are created by CD — see below.

---

## Cloud Scheduler jobs (created by CD)

The last deploy step, **Apply Cloud Scheduler jobs**, runs `python3 -m infrastructure.scheduler.apply_scheduler_jobs` after traffic shifts to the new revision. For each job it runs `gcloud scheduler jobs describe`; if the job exists it is updated (`--update-headers`), otherwise it is created (`--headers`). Decision record: [ADR 0005](./adrs/0005-cloud-scheduler-from-cd.md).

| Job | Cron | Timezone | Target |
|-----|------|----------|--------|
| `wine-send-recommendations` | `0 10 * * 4,6` (Thursday and Saturday 10:00) | `America/Sao_Paulo` | `POST {SERVICE_URL}/jobs/send-recommendations` |
| `wine-send-weekly-education` | `0 15 * * 1` (Monday 15:00) | `America/Sao_Paulo` | `POST {SERVICE_URL}/jobs/send-weekly-education` |

- **Location:** `southamerica-east1` (same as `REGION`). `SERVICE_URL` is read with `gcloud run services describe wine-concierge --format=value(status.url)`.
- **Headers:** `X-Job-Internal-Secret=<secret>` and `Content-Type=application/json`.
- **Scheduler retries:** `--max-retry-attempts=3`, `--min-backoff=60s`, `--max-backoff=600s`, `--attempt-deadline=300s`. A retried recommendation run skips customers sent to in the last 24h ([entry-recommendation-cadence-sdd.md](./specs/entry-recommendation-cadence-sdd.md)).
- **Secret:** read at deploy time from Secret Manager secret **`wine-concierge-job-internal-secret`** (workflow env `JOB_INTERNAL_SECRET_ID`). The step masks the value in the Actions log and never prints it.
- **CD failure:** the step makes up to 3 attempts (waiting 10s, then 20s). If all fail, the deploy workflow fails.
- **Rotation:** after adding a new secret version, redeploy (tag) or run the deploy workflow with `workflow_dispatch` so the Scheduler header picks up the new value.

**Prerequisites (ops, not automated):**

- Cloud Scheduler API enabled: `gcloud services enable cloudscheduler.googleapis.com --project=wineia-490200`
- Deploy service account has `roles/cloudscheduler.admin`.
- Deploy service account has `roles/secretmanager.secretAccessor` on `wine-concierge-job-internal-secret`.

---

## Docker image

Built from repo `Dockerfile`:

- Base: `python:3.11-slim`
- CMD: `gunicorn -b 0.0.0.0:8080 main:app`

CI validates build without push in `.github/workflows/docker.yml`.

---

## Configuration at runtime

Set Cloud Run environment variables / secrets for:

- Twilio: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_FROM`
- GCP: `PROJECT_ID`, `QUEUE_REGION`, `SERVICE_URL` (for task enqueue URLs)
- Anthropic / IA keys as required by `infrastructure/external/claude_client.py`
- **`JOB_INTERNAL_SECRET`** — shared secret for internal job and worker HTTP endpoints (see below)

Use Secret Manager for sensitive values in production. **Mapping, IAM, and cutover steps:** [operations/SECRET-MANAGER-MIGRATION.md](./operations/SECRET-MANAGER-MIGRATION.md) (ADR [0004](./adrs/0004-secret-manager-runtime-secrets.md)).

**Threat model** (trust boundaries, webhook/job/LLM risks): [threat-model.md](./threat-model.md).

### `JOB_INTERNAL_SECRET` (jobs and workers)

Paths under **`/jobs/*`** and **`/workers/*`** require a valid shared secret. Public callers without the secret receive **401 Unauthorized**.

| Item | Value |
|------|--------|
| Environment variable | `JOB_INTERNAL_SECRET` |
| Request header | `X-Job-Internal-Secret` |
| Enforced in | `api/routes.py` via `api/internal_job_auth.py` |

**Generate a value** (example):

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Cloud Run:** set `JOB_INTERNAL_SECRET` on the `wine-concierge` service (Secret Manager reference recommended).

**Cloud Scheduler:** CD writes header `X-Job-Internal-Secret` on both job targets from Secret Manager — see [Cloud Scheduler jobs (created by CD)](#cloud-scheduler-jobs-created-by-cd).

**Cloud Tasks:** when `JOB_INTERNAL_SECRET` is set on the Cloud Run runtime, `CloudTasksClient.enqueue` automatically adds `X-Job-Internal-Secret` to worker task HTTP requests.

If `JOB_INTERNAL_SECRET` is **unset**, job and worker routes reject all requests (fail closed).

### WhatsApp webhook rate limits

`POST /webhook/whatsapp` only. Spec: [specs/webhook-rate-limit.md](./specs/webhook-rate-limit.md).

| Environment variable | Default | Meaning |
|----------------------|---------|---------|
| `WEBHOOK_RATE_LIMIT_IP_MAX` | `120` | Max requests per client IP per window (`0` = off) |
| `WEBHOOK_RATE_LIMIT_IP_WINDOW_SECONDS` | `60` | IP window length (seconds) |
| `WEBHOOK_RATE_LIMIT_PHONE_MAX` | `30` | Max requests per sender phone per window (`0` = off) |
| `WEBHOOK_RATE_LIMIT_PHONE_WINDOW_SECONDS` | `60` | Phone window length (seconds) |

When exceeded, the API returns **429** with `{"error":"rate_limit_exceeded"}`. IP is checked in the router; phone is checked after a valid Twilio signature.

### On-demand IA daily caps (per plan tier)

Product entitlements for inbound WhatsApp IA (not webhook abuse limits). Spec: [specs/on-demand-entitlements-sdd.md](./specs/on-demand-entitlements-sdd.md), [specs/sdd/T060-per-tier-ia-caps-sdd.md](./specs/sdd/T060-per-tier-ia-caps-sdd.md).

| Environment variable | Default | Meaning |
|----------------------|---------|---------|
| `ON_DEMAND_DAILY_LIMIT_ENTRY` | `2` | Max on-demand IA replies per UTC day for `ENTRY` |
| `ON_DEMAND_DAILY_LIMIT_SUPERIOR` | `10` | Max on-demand IA replies per UTC day for `SUPERIOR` |

Unset, empty, non-integer, or negative values fall back to the defaults. `0` is valid (blocks all on-demand IA for that tier). Read through `core/config.py` into `domain/on_demand_entitlements.py`.

### Global Claude daily call budget

Fleet-wide ceiling on successful Claude API calls per UTC calendar day (not USD). Spec: [specs/sdd/T061-global-claude-budget-stop-sdd.md](./specs/sdd/T061-global-claude-budget-stop-sdd.md).

| Environment variable | Default | Meaning |
|----------------------|---------|---------|
| `CLAUDE_DAILY_CALL_BUDGET` | `0` | Max Claude API calls per UTC day. **`0` or unset = unlimited** (local/dev safe). |

Unset, empty, non-integer, or negative values fall back to `0` (unlimited). When `> 0`, new generations fail closed before calling Claude once today's count is exhausted. Counter increments only after a successful generate. Ops map call volume → cost via Anthropic billing offline.

**Production recommendation:** set a positive ceiling so a runaway day cannot burn unlimited Anthropic quota. Suggested starting value: **`500`** calls per UTC day — an **ops-tunable guess**, not a hard product constant. Raise or lower after watching Cloud Run logs and Anthropic billing. Leaving `0` in production means unlimited.

### Privacy policy and terms URLs (opt-in notice)

Used in the Portuguese privacy/terms notice returned at pre-sale create and activation. Spec: [specs/sdd/T050-privacy-terms-opt-in-sdd.md](./specs/sdd/T050-privacy-terms-opt-in-sdd.md).

| Environment variable | Default | Meaning |
|----------------------|---------|---------|
| `PRIVACY_POLICY_URL` | `https://example.com/privacy` | Public privacy policy link in opt-in notice |
| `TERMS_OF_SERVICE_URL` | `https://example.com/terms` | Public terms of service link in opt-in notice |

Unset or empty/whitespace values fall back to the placeholders above. Missing production URLs do **not** block pre-sale registration in MVP; replace placeholders before launch.

### WhatsApp webhook outbound (async replies)

Inbound `POST /webhook/whatsapp` still validates the Twilio signature and generates Claude copy in the request. Product WhatsApp text (IA reply and daily-limit warning) is **enqueued** on Cloud Tasks queue `wine-messages` (`send_message` → `POST /workers/send-message`). Cancel (`cancelar`) updates Datastore only and sends no outbound text.

**Twilio retries:** Twilio retries inbound webhooks on non-2xx responses or timeouts. After enqueue succeeds, the webhook returns **200** `{"status":"received"}` even if the worker has not yet delivered WhatsApp. A **200** means Twilio will **not** HTTP-retry that delivery attempt; late send failures are handled by Cloud Tasks / the worker, not by a second webhook POST. Operators must not expect a Twilio retry to finish a send that was already accepted for enqueue. Requires `SERVICE_URL` and `PROJECT_ID` on Cloud Run (same as scheduled enqueue).

---

## Rollback

Cloud Run keeps revisions. To rollback traffic:

```bash
gcloud run services update-traffic wine-concierge \
  --to-revisions=<previous-revision>=100 \
  --region=southamerica-east1 \
  --project=wineia-490200
```

Or redeploy a prior image tag from Artifact Registry.

---

## Related docs

- [ROADMAP.md](./ROADMAP.md) — M0 deploy items, M5 queue/scheduler gaps
- [ENGINEERING_MANUAL.md](./ENGINEERING_MANUAL.md)
- [GIT_WORKFLOW.md](./GIT_WORKFLOW.md) — release tagging
