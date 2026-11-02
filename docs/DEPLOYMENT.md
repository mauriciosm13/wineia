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
- `wine-campaigns` → worker `/workers/send-campaign` (not yet implemented)

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
- Cloud Scheduler jobs (e.g. `daily-recommendations`) are **not yet created by CD** — provision manually or extend deploy workflow later.

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

**Cloud Scheduler** (e.g. `POST /jobs/send-recommendations`): add header `X-Job-Internal-Secret: <value>` on the HTTP target. Use Scheduler’s secret/header configuration or store the value in Secret Manager and reference it in the job definition.

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
