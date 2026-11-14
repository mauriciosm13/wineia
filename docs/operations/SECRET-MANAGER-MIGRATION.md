# Secret Manager migration — WineAI production

**Task:** T011 · **Commercial launch:** Phase 2 #8  
**Status:** Plan approved (ops cutover follows phases below)  
**ADR:** [0004-secret-manager-runtime-secrets.md](../adrs/0004-secret-manager-runtime-secrets.md)

This document is the **operator runbook** for moving sensitive production values from plain Cloud Run environment variables and ad hoc files into **Google Secret Manager**, without changing application behavior in the migration PR itself.

---

## Goals

1. **No long-lived secrets** in repo, deploy scripts, or GitHub (except OIDC/WIF — already keyless per ADR 0001).
2. **Same env var names** at runtime so Python code in `core/config.py` and callers keep working during cutover.
3. **Auditable rotation** via Secret Manager versions and Cloud Run revision updates.
4. **Clear split:** local dev stays on gitignored `config.json`; production uses Secret Manager only.

---

## Current state (inventory)

### Sensitive values

| Consumer | Source today | Env / key | Sensitive |
|----------|--------------|-----------|-----------|
| Twilio webhook signature | `core/config.py` | `TWILIO_AUTH_TOKEN` | Yes |
| Twilio REST (partial path) | `core/config.py` | `TWILIO_ACCOUNT_SID`, `TWILIO_WHATSAPP_FROM` | SID/from: low; token: yes |
| Twilio REST (legacy path) | `config.json` via `load_config()` | `account_sid`, `auth_token`, `numberTwillio` | Yes |
| Claude API | `config.json` | `ANTHROPIC_API_KEY`, `ANTHROPIC_API_MODEL` | Key: yes; model: no |
| Job/worker auth | `core/config.py` | `JOB_INTERNAL_SECRET` | Yes |
| Legacy Meta WhatsApp | `core/config.py` | `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_ID` | Yes (if used) |

### Non-secret configuration (stay plain env on Cloud Run)

| Variable | Purpose |
|----------|---------|
| `PROJECT_ID` | GCP project (`wineia-490200`) |
| `QUEUE_REGION` | Cloud Tasks region (`southamerica-east1`) |
| `SERVICE_URL` | Base URL for task enqueue (`infrastructure/queue/cloud_tasks_client.py`) |
| `TWILIO_TIMEOUT` | HTTP timeout (default `30`) |
| `ANTHROPIC_API_MODEL` | Model id (non-secret; may stay env or move to secret for consistency — optional) |

### Gaps to close after this plan (separate PRs)

- **Unify Twilio config:** webhook uses env; some send paths still read `config.json`. Production should set **both** env vars and stop shipping `config.json` in the image (already excluded via `.gcloudignore` / `.gitignore` — operators must not bake secrets into the image).
- **Claude client:** `infrastructure/external/claude_client.py` reads only `config.json` today. Cutover requires either mounting secrets into env and extending config loading, or documenting that ops inject `config.json` at deploy (discouraged). **Recommended follow-up:** read `ANTHROPIC_API_KEY` from env with `config.json` fallback for local dev.

---

## Target Secret Manager layout

**Project:** `wineia-490200`  
**Naming convention:** `wine-concierge/<slug>` where `<slug>` is a lowercase kebab case of the purpose.

> **Note:** Secret Manager secret IDs may contain only letters, digits, `-`, and `_`; they cannot contain `/`. The `wine-concierge/...` IDs below are not valid as written. Ops must confirm the real IDs before running the examples.
>
> **CD:** the deploy workflow reads the job secret from `wine-concierge-job-internal-secret` (workflow env `JOB_INTERNAL_SECRET_ID`) and writes it as the Cloud Scheduler `X-Job-Internal-Secret` header — [ADR 0005](../adrs/0005-cloud-scheduler-from-cd.md).

| Secret Manager secret id | Cloud Run env var | Notes |
|--------------------------|-------------------|--------|
| `wine-concierge/twilio-auth-token` | `TWILIO_AUTH_TOKEN` | Webhook + API |
| `wine-concierge/twilio-account-sid` | `TWILIO_ACCOUNT_SID` | Optional if kept plain env |
| `wine-concierge/twilio-whatsapp-from` | `TWILIO_WHATSAPP_FROM` | E.164 / Twilio sender |
| `wine-concierge/anthropic-api-key` | `ANTHROPIC_API_KEY` | Requires code follow-up to read env |
| `wine-concierge/job-internal-secret` | `JOB_INTERNAL_SECRET` | Same value for Scheduler/Tasks headers |
| `wine-concierge/whatsapp-token` | `WHATSAPP_TOKEN` | Only if Meta path enabled |
| `wine-concierge/whatsapp-phone-id` | `WHATSAPP_PHONE_ID` | Only if Meta path enabled |

**Scheduler / manual job calls:** store the same material as `wine-concierge/job-internal-secret`. Configure Cloud Scheduler HTTP target header `X-Job-Internal-Secret` from Secret Manager (Scheduler secret resource or synced value — see [DEPLOYMENT.md](../DEPLOYMENT.md#job_internal_secret-jobs-and-workers)).

**Do not** duplicate Twilio credentials in `config.json` on Cloud Run once env + secrets are set.

---

## IAM

**Runtime service account** (the identity Cloud Run uses to run `wine-concierge`, e.g. `wine-concierge@wineia-490200.iam.gserviceaccount.com` — confirm in console):

| Role | Purpose |
|------|---------|
| `roles/secretmanager.secretAccessor` | Read secret versions mounted into the service |

Grant **per secret** or at project level for this SA only (prefer per-secret for least privilege).

**Deploy service account** (GitHub WIF): needs `roles/secretmanager.secretAccessor` on `wine-concierge-job-internal-secret`, because the deploy workflow reads it to configure the Cloud Scheduler header ([ADR 0005](../adrs/0005-cloud-scheduler-from-cd.md)). If the workflow starts passing `--set-secrets`, it also needs `secretAccessor` on the referenced secrets.

**Operators (humans):** `roles/secretmanager.admin` or `secretAccessor` + `secretmanager.versions.add` for rotation — not the runtime SA.

---

## Rollout phases

### Phase A — Prepare secrets (no traffic impact)

1. Enable Secret Manager API if not already enabled:
   ```bash
   gcloud services enable secretmanager.googleapis.com --project=wineia-490200
   ```
2. For each row in the mapping table, create the secret and add version **1** from a secure channel (never commit values):
   ```bash
   printf '%s' "$VALUE" | gcloud secrets create wine-concierge/twilio-auth-token \
     --project=wineia-490200 \
     --replication-policy=automatic \
     --data-file=-
   ```
   If the secret already exists, add a new version:
   ```bash
   printf '%s' "$VALUE" | gcloud secrets versions add wine-concierge/twilio-auth-token \
     --project=wineia-490200 \
     --data-file=-
   ```
3. Grant the Cloud Run runtime SA `secretAccessor` on each secret.

### Phase B — Mount on Cloud Run (new revision)

Mount secrets as **environment variables** (recommended for this codebase):

```bash
gcloud run services update wine-concierge \
  --region=southamerica-east1 \
  --project=wineia-490200 \
  --set-secrets="TWILIO_AUTH_TOKEN=wine-concierge/twilio-auth-token:latest,TWILIO_ACCOUNT_SID=wine-concierge/twilio-account-sid:latest,TWILIO_WHATSAPP_FROM=wine-concierge/twilio-whatsapp-from:latest,JOB_INTERNAL_SECRET=wine-concierge/job-internal-secret:latest"
```

Add `ANTHROPIC_API_KEY=wine-concierge/anthropic-api-key:latest` **after** the code reads that env var (follow-up PR).

**Remove** any plain-text values for the same keys from `--set-env-vars` / console env to avoid override confusion. Cloud Run secret refs take precedence when configured correctly; delete duplicate plain env entries.

Deploy workflow (`.github/workflows/deploy.yml`) today does **not** set secrets — ops cutover is manual or a future CD change. Document any manual revision in the deploy log.

### Phase C — Callers of `JOB_INTERNAL_SECRET`

1. **Cloud Scheduler:** point HTTP header `X-Job-Internal-Secret` at the same secret version (or paste once from SM during job setup).
2. **Cloud Tasks:** no change if tasks are enqueued from Cloud Run with `JOB_INTERNAL_SECRET` set — `CloudTasksClient` adds the header automatically.
3. **Manual curl:** read secret via `gcloud secrets versions access latest --secret=wine-concierge/job-internal-secret`.

### Phase D — Verify

| Check | Expected |
|-------|----------|
| `GET /health` | 200 |
| Twilio webhook with valid signature | 200 / app logic |
| `POST /jobs/send-recommendations` without header | 401 |
| With `X-Job-Internal-Secret` | 200 or business response |
| Logs | No secret values printed (existing logging should remain metadata-only) |

### Phase E — Decommission plain env

After one stable revision, remove obsolete plain env vars from prior revisions documentation and rotate any secret that ever lived in plain env (treat as potentially leaked).

---

## Rotation

1. Add secret version **N+1** in Secret Manager.
2. Update Cloud Run to `:latest` or pin `:N+1` explicitly:
   ```bash
   gcloud run services update wine-concierge ... --set-secrets=TWILIO_AUTH_TOKEN=wine-concierge/twilio-auth-token:2
   ```
3. For `JOB_INTERNAL_SECRET`, update Scheduler header and wait for in-flight tasks to drain.
4. Disable/delete old secret versions after soak period.

---

## Rollback

1. **Traffic:** shift to previous Cloud Run revision (see [DEPLOYMENT.md](../DEPLOYMENT.md#rollback)).
2. **Secrets:** revert `--set-secrets` to prior version numbers or temporary plain env (emergency only; rotate after incident).

---

## Local development (unchanged)

- Copy [`config.example.json`](../../config.example.json) → `config.json` (gitignored).
- Export env vars as documented in [README.md](../../README.md) when testing Twilio webhook paths.
- Secret Manager is **not** required locally.

---

## Related

- [DEPLOYMENT.md](../DEPLOYMENT.md) — Cloud Run, WIF, `JOB_INTERNAL_SECRET`
- [PRODUCTION.md](./PRODUCTION.md) — live service reference
- [INCIDENT-RESPONSE.md](./INCIDENT-RESPONSE.md) — if cutover causes auth failures
