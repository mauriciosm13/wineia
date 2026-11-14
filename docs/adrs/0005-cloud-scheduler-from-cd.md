# ADR 0005: Cloud Scheduler jobs provisioned by CD

**Status:** Accepted  
**Date:** 2026-11-14  
**Deciders:** WineAI team  
**Related:** T031 · [COMMERCIAL-LAUNCH.md](../COMMERCIAL-LAUNCH.md) #27 · [T031 SDD](../specs/sdd/T031-scheduler-deploy-cd-sdd.md) · [ADR 0004](./0004-secret-manager-runtime-secrets.md)

---

## Context

`POST /jobs/send-recommendations` and `POST /jobs/send-weekly-education` require the `X-Job-Internal-Secret` header (`api/internal_job_auth.py`), but nothing calls them on a schedule. The deploy workflow (`.github/workflows/deploy.yml`) builds the image, deploys Cloud Run, and shifts traffic; it creates no Cloud Scheduler job. Manually created jobs drift from the repo and are easy to forget after a rebuild of the project.

The job secret lives in Secret Manager (ADR 0004). The deploy workflow authenticates with GitHub OIDC (ADR 0001) and has no GitHub-stored application secrets.

---

## Decision

1. **CD provisions Cloud Scheduler.** The final deploy step runs `python3 -m infrastructure.scheduler.apply_scheduler_jobs` after traffic shifts. It creates or updates exactly two jobs in `REGION`:
   - `wine-send-recommendations` — `0 10 * * 4,6` `America/Sao_Paulo` → `POST /jobs/send-recommendations`
   - `wine-send-weekly-education` — `0 15 * * 1` `America/Sao_Paulo` → `POST /jobs/send-weekly-education`
2. **Header from Secret Manager at deploy time.** The step reads `wine-concierge-job-internal-secret` (workflow env `JOB_INTERNAL_SECRET_ID`) with `gcloud secrets versions access latest` and writes it as a static `X-Job-Internal-Secret` header on both jobs. The value is masked in the Actions log and never printed. No OIDC token on the Scheduler target and no change to application auth.
3. **Retries.** Scheduler retries each run up to 3 times (`--max-retry-attempts=3`, `--min-backoff=60s`, `--max-backoff=600s`, `--attempt-deadline=300s`). The recommendation job skips customers sent to in the last 24h, so a retry never sends twice.
4. **CD failure.** The step makes up to 3 attempts; if all fail, the deploy workflow fails.
5. **Standard library only.** The module calls `gcloud` through `subprocess`; the deploy job installs no Python dependencies.

### Prerequisites (ops, not automated)

- Cloud Scheduler API enabled in `wineia-490200`.
- Deploy service account has `roles/cloudscheduler.admin`.
- Deploy service account has `roles/secretmanager.secretAccessor` on the job secret.

---

## Consequences

### Positive

- Schedules, targets, and retry policy are versioned in the repo and re-applied on every deploy
- No secret in GitHub, the workflow YAML, or job logs
- No application change: the jobs use the same header as manual calls

### Negative

- Anyone who can view the Scheduler job (`cloudscheduler.jobs.get`) sees the header value
- Rotating the secret needs a redeploy or a `workflow_dispatch` run so the jobs pick up the new value
- The deploy service account gains Scheduler admin and read access to one secret

### Neutral

- Prerequisites and runbook in [DEPLOYMENT.md](../DEPLOYMENT.md#cloud-scheduler-jobs-created-by-cd)

---

## Alternatives

| Alternative | Why not chosen |
|-------------|----------------|
| OIDC token on the Scheduler target | Needs an app auth change and a Scheduler invoker identity; out of scope for T031 |
| Runbook-only (ops create jobs by hand) | Drifts from the repo; easy to miss after a rebuild; no review of schedule changes |

---

## References

- [Cloud Scheduler: create HTTP target jobs](https://cloud.google.com/scheduler/docs/creating)
- [GitHub Actions: masking a value in a log](https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#masking-a-value-in-a-log)
