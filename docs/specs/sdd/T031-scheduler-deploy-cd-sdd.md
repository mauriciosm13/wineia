# SDD — Scheduler jobs in deploy/CD (T031)

**Status:** implemented  
**Task:** [T031](../../ROADMAP-TASKS.md)  
**Comparison contract:** this Expected work list is what the reviewer checks against [T031-builder-report.md](./T031-builder-report.md).

## Problem

`POST /jobs/send-recommendations` and `POST /jobs/send-weekly-education` exist, but nothing calls them on a schedule. `deploy.yml` builds, deploys Cloud Run, and shifts traffic. It creates no Cloud Scheduler job.

Two domain rules would also make customers lose messages once a fixed weekly schedule exists:

1. **Window boundary.** `roll_recommendation_window_if_expired` rolls only at `now - start >= 168h`, and the window starts at the previous run's `now_utc`. A weekly run that starts seconds earlier than last week is still inside the window, so the customer is skipped. With Thursday and Saturday runs, every following Thursday hits this. `is_eligible_for_weekly_education` has the same problem with its exact 7-day cooldown, and `last_weekly_education_at` is stamped after the Claude call, so it fails about every other week.
2. **Retries.** If a recommendation run fails partway, a Scheduler retry runs the loop again. Customers already enqueued have `recommendation_send_count_7d == 1`, which is still `< 2`, so they get a second message in the same slot and lose their next slot.

## Goals

- CD creates or updates exactly two Cloud Scheduler jobs on every production deploy.
- Every scheduled run sends each eligible customer at most one message, including when retried.
- A customer on the Thursday/Saturday schedule gets both messages every week.
- The secret never appears in the repo, the workflow YAML, or job logs.

## Non-goals

- OIDC on Scheduler or any app auth change.
- Cloud Run flags, `--set-secrets`, `deploy.sh`.
- Scheduling workers or a campaign producer.
- Legacy window migration (`migrate_recommendation_window_from_legacy`).
- Granting IAM or enabling APIs (documented prerequisites only).
- New pip dependencies. `docs/MVP_SCOPE.md`.
- Reordering enqueue and Datastore update in the job loops. Known residual risk: if `update` raises after a successful enqueue, that one customer's send is not recorded and a retry resends to them. Track separately.
- Changing how `send_weekly_education` stamps or reads time. The 6h grace absorbs the drift.

## Behavior

### Scheduler jobs

| Job name | Cron | Timezone | Target |
|----------|------|----------|--------|
| `wine-send-recommendations` | `0 10 * * 4,6` | `America/Sao_Paulo` | `POST {SERVICE_URL}/jobs/send-recommendations` |
| `wine-send-weekly-education` | `0 15 * * 1` | `America/Sao_Paulo` | `POST {SERVICE_URL}/jobs/send-weekly-education` |

Both jobs: location = `REGION`, headers `X-Job-Internal-Secret=<secret>` and `Content-Type=application/json`, `--max-retry-attempts=3`, `--min-backoff=60s`, `--max-backoff=600s`, `--attempt-deadline=300s`.

### Domain

| Constant | Value | Rule |
|----------|-------|------|
| `RECOMMENDATION_WINDOW_GRACE` | 6h | Window rolls when `now - start >= 168h - 6h` |
| `RECOMMENDATION_RETRY_GUARD` | 24h | Skip when `now - last_recommendation_at < 24h` |
| `WEEKLY_EDUCATION_GRACE` | 6h | Eligible when `now - last >= 7d - 6h` |

### CD step

1. After "Shift traffic to latest revision", run `python3 -m infrastructure.scheduler.apply_scheduler_jobs`.
2. The module reads the secret (`gcloud secrets versions access latest --secret=$JOB_INTERNAL_SECRET_ID`), prints `::add-mask::<secret>` before any other output, and reads the service URL (`gcloud run services describe $SERVICE --format=value(status.url)`).
3. For each job: `describe` → if found `update http` (with `--update-headers`), otherwise `create http` (with `--headers`).
4. Steps 2–3 are one attempt. Up to 3 attempts, waiting 10s then 20s. After the third failure, exit non-zero and the workflow fails.

## Expected work

The builder implements only these items. The reviewer marks each **match**, **gap**, or **extra**.

| ID | Must be true when the work is done | Where |
|----|-------------------------------------|--------|
| EW-01 | `RECOMMENDATION_WINDOW_GRACE = timedelta(hours=6)`. `roll_recommendation_window_if_expired` rolls when `now - start >= ROLLING_RECOMMENDATION_WINDOW - RECOMMENDATION_WINDOW_GRACE`. Test: start Thu 10:00:30 UTC, `last_recommendation_at` older than 24h, count 2, now next Thu 10:00:00 → rolls and send is allowed. Test: `now = start + 161h59m` with count 2 → no roll, send denied. | `domain/recommendation_scheduled_cadence.py`, `tests/unit/domain/test_recommendation_scheduled_cadence.py` |
| EW-02 | `RECOMMENDATION_RETRY_GUARD = timedelta(hours=24)`. `should_send_scheduled_recommendation` returns False when `last_recommendation_at` is set and `now - last < 24h`, even when count < 2. Test: a run 5 minutes after a send skips the customer. Test: a run 48h later (Saturday) still sends. | same files |
| EW-03 | `WEEKLY_EDUCATION_GRACE = timedelta(hours=6)`. `is_eligible_for_weekly_education` is True when `now - last >= WEEKLY_EDUCATION_COOLDOWN - WEEKLY_EDUCATION_GRACE`. Test: last Mon 15:00:20, now next Mon 15:00:05 → eligible. Test: `now = last + 6d17h59m` → not eligible. | `domain/services/education_eligibility.py`, `tests/unit/domain/test_education_eligibility.py` |
| EW-04 | Scenario test over 4 weeks using only the cadence functions: Thursday and Saturday runs at 10:00 America/Sao_Paulo (13:00 UTC), each later run starting up to 60s earlier than the previous one, plus a retry 5 minutes after every Thursday run. The customer gets exactly 8 sends, one per scheduled slot, and no retry ever sends. | `tests/unit/domain/test_recommendation_scheduled_cadence.py` |
| EW-05 | `infrastructure/scheduler/apply_scheduler_jobs.py` defines exactly the two jobs in the Behavior table (names, cron, timezone, path, POST) and the retry flags. Standard library only. `infrastructure/scheduler/__init__.py` exists. | `infrastructure/scheduler/` |
| EW-06 | Create-or-update: `describe` success → `gcloud scheduler jobs update http` with `--update-headers`; `describe` failure → `gcloud scheduler jobs create http` with `--headers`. Both pass `--location`, `--project`, `--schedule`, `--time-zone`, `--uri`, `--http-method=POST`, both headers, and the four retry/deadline flags. Unit tests with a fake runner assert the argv for both branches and both jobs. | module + `tests/unit/infrastructure/test_apply_scheduler_jobs.py` |
| EW-07 | Secret and URL come from `gcloud` via the runner. The first line written to stdout is `::add-mask::<secret>`. No other output line contains the secret. An empty secret or empty URL fails the attempt. Tests assert all three. | same |
| EW-08 | One attempt = read secret + read URL + apply both jobs. Up to 3 attempts with waits of 10s and 20s (sleep injectable). Fails twice then succeeds → exit 0, 3 attempts. Fails three times → non-zero exit, no fourth attempt. Tests assert both. | same |
| EW-09 | `deploy.yml` adds env `JOB_INTERNAL_SECRET_ID: wine-concierge-job-internal-secret` and a step after "Shift traffic to latest revision" that runs `python3 -m infrastructure.scheduler.apply_scheduler_jobs` with `PROJECT_ID`, `REGION`, `SERVICE`, `JOB_INTERNAL_SECRET_ID`. No secret value in YAML, no `set -x`, no `continue-on-error`. Triggers unchanged. Earlier steps unchanged. | `.github/workflows/deploy.yml` |
| EW-10 | ADR 0005 records: Scheduler provisioned by CD; header sourced from Secret Manager at deploy time; prerequisites (Cloud Scheduler API enabled; deploy SA `roles/cloudscheduler.admin` and `roles/secretmanager.secretAccessor` on the job secret); consequences (anyone who can view the job sees the header; rotating the secret needs a redeploy or `workflow_dispatch`); alternatives (OIDC, runbook-only). | `docs/adrs/0005-cloud-scheduler-from-cd.md` |
| EW-11 | Docs: `DEPLOYMENT.md` scheduler section (jobs table, retries, IAM prerequisites, secret ID, rotation). `PRODUCTION.md` lists both jobs. `SECRET-MANAGER-MIGRATION.md` notes that secret IDs cannot contain `/`, that CD reads `wine-concierge-job-internal-secret`, and its IAM section no longer says the deploy SA needs no Secret Manager access. `entry-recommendation-cadence-sdd.md` documents the 6h grace and 24h guard. `weekly-education-job.md` documents the 6h grace and the Monday 15:00 schedule. `README.md` Gaps no longer lists Scheduler-from-CD. `ROADMAP.md` checks "Scheduler created by CD". | those files |
| EW-12 | Only after EW-01–EW-11 and EW-13 hold: `ROADMAP-TASKS.md` checks T031, `COMMERCIAL-LAUNCH.md` checks item 27, this SDD status is `implemented`, and `INDEX.md` matches. | those files |
| EW-13 | Diff does not touch `api/internal_job_auth.py`, Cloud Run deploy flags, `deploy.sh`, `requirements*.txt`, `docs/MVP_SCOPE.md`, on-demand entitlements, or `migrate_recommendation_window_from_legacy`. Domain/core coverage stays ≥ 95%. | whole diff |

## Builder report

After implementation, write `docs/specs/sdd/T031-builder-report.md`:

| ID | Result (`done` or `skipped`) | Files | What changed |
|----|-------------------------------|-------|----------------|

Add a **Files touched** list of every path in the diff and the exact test commands with results. The reviewer treats any path not justified by an ID as **extra**.

## Reviewer comparison

Read this file, the builder report, and the diff. Return only:

- One line per ID: `EW-xx match|gap — evidence`
- Extras: paths or behavior not in the table
- Bugs that break an ID or would make a customer lose or duplicate a message
- Verdict: accept or reject

Do not implement.

## Related

- [CONTEXT.md](../../../CONTEXT.md)
- [entry-recommendation-cadence-sdd.md](../entry-recommendation-cadence-sdd.md)
- [weekly-education-job.md](../weekly-education-job.md)
- [DEPLOYMENT.md](../../DEPLOYMENT.md)
- [SECRET-MANAGER-MIGRATION.md](../../operations/SECRET-MANAGER-MIGRATION.md)
- [ADR 0004](../../adrs/0004-secret-manager-runtime-secrets.md)

## Revision history

| Date | Change |
|------|--------|
| 2026-11-10 | Initial stub |
| 2026-11-14 | Orchestrator checklist EW-01–EW-13 from user decisions (Thu/Sat 10:00 and Mon 15:00, Secret Manager header, 3 retries + 24h guard, 6h grace, CD fails after 3 attempts) |
