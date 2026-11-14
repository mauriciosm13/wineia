# SPEC — T031 Scheduler jobs in deploy/CD

**Status:** ready for implementation
**Task:** T031 ([docs/ROADMAP-TASKS.md](docs/ROADMAP-TASKS.md))
**Branch:** `feat/t031-scheduler-cd` (exists). No commit and no push until the orchestrator asks.
**Binding sources:** [CONTEXT.md](CONTEXT.md), [PLAN.md](PLAN.md), [docs/specs/sdd/T031-scheduler-deploy-cd-sdd.md](docs/specs/sdd/T031-scheduler-deploy-cd-sdd.md) (Expected work EW-01–EW-13).
**Decisions:** approved by the user on 2026-11-14 (recorded in CONTEXT.md). This spec adds no requirement beyond EW-01–EW-13.

This file is the implementation contract. If it ever disagrees with the SDD Expected work table, the SDD wins.

## Problem

`POST /jobs/send-recommendations` and `POST /jobs/send-weekly-education` exist, but nothing calls them on a schedule. `.github/workflows/deploy.yml` builds, deploys Cloud Run, and shifts traffic. It creates no Cloud Scheduler job.

Once a fixed weekly schedule exists, two domain rules would make customers lose messages:

1. **Window boundary.** `roll_recommendation_window_if_expired` rolls only at `now - start >= 168h`, and the window starts at the previous run's `now_utc`. A weekly run that starts seconds earlier than last week is still inside the window, so the customer is skipped on every following Thursday. `is_eligible_for_weekly_education` has the same problem with its exact 7-day cooldown, made worse because `last_weekly_education_at` is stamped after the Claude call.
2. **Retries.** If a recommendation run fails partway, a Scheduler retry runs the loop again. Customers already enqueued have `recommendation_send_count_7d == 1`, still `< 2`, so they get a second message in the same slot and lose their next slot.

## Goals

- CD creates or updates exactly two Cloud Scheduler jobs on every production deploy.
- Every scheduled run sends each eligible customer at most one message, including when retried.
- A customer on the Thursday/Saturday schedule gets both messages every week.
- The secret never appears in the repo, the workflow YAML, or job logs.

## Scope

| Slice | EW | Files |
|-------|----|-------|
| Recommendation window grace | EW-01 | `domain/recommendation_scheduled_cadence.py`, `tests/unit/domain/test_recommendation_scheduled_cadence.py` |
| Recommendation retry guard | EW-02 | same |
| Weekly education grace | EW-03 | `domain/services/education_eligibility.py`, `tests/unit/domain/test_education_eligibility.py` |
| Four-week Thursday/Saturday scenario | EW-04 | `tests/unit/domain/test_recommendation_scheduled_cadence.py` |
| Scheduler apply module and job table | EW-05 | `infrastructure/scheduler/__init__.py`, `infrastructure/scheduler/apply_scheduler_jobs.py` |
| Create-or-update argv | EW-06 | apply module, `tests/unit/infrastructure/test_apply_scheduler_jobs.py` |
| Secret mask and service URL | EW-07 | same |
| Three CD attempts | EW-08 | same |
| Deploy workflow step | EW-09 | `.github/workflows/deploy.yml` |
| ADR 0005 | EW-10 | `docs/adrs/0005-cloud-scheduler-from-cd.md` |
| Ops and behavior docs | EW-11 | `docs/DEPLOYMENT.md`, `docs/operations/PRODUCTION.md`, `docs/operations/SECRET-MANAGER-MIGRATION.md`, `docs/specs/entry-recommendation-cadence-sdd.md`, `docs/specs/weekly-education-job.md`, `README.md`, `docs/ROADMAP.md` |
| Status flips | EW-12 | `docs/ROADMAP-TASKS.md`, `docs/COMMERCIAL-LAUNCH.md`, `docs/specs/sdd/T031-scheduler-deploy-cd-sdd.md`, `docs/specs/sdd/INDEX.md` |
| Diff and coverage gate | EW-13 | whole diff |
| Builder report | EW-01–EW-13 | `docs/specs/sdd/T031-builder-report.md` |

`PLAN.md` and this `SPEC.md` are handoff files, not T031 deliverables. Do not list them as Expected work products in the builder report.

## Out of scope

- OIDC tokens on Scheduler, or any change to `api/internal_job_auth.py`.
- Cloud Run deploy flags, `--set-secrets`, or `deploy.sh`.
- Scheduling `/workers/*` or a campaign producer.
- On-demand entitlements (T024/T060/T061) and async webhook replies (T032).
- `migrate_recommendation_window_from_legacy` behavior. It keeps comparing against the full 168h.
- New pip dependencies; any change to `requirements*.txt`.
- `docs/MVP_SCOPE.md`.
- Reordering enqueue vs Datastore update in job loops. Known residual risk: if `update` raises after a successful enqueue, that customer's send is not recorded and a retry resends. Tracked separately.
- How `send_weekly_education` stamps or reads time. The 6h grace absorbs the drift.
- Changes to `domain/services/recommendation_service.py` or `record_scheduled_recommendation_send`.
- Creating GCP IAM bindings or enabling APIs. These are documented prerequisites only.
- In `docs/operations/SECRET-MANAGER-MIGRATION.md`: renaming the other `wine-concierge/...` example IDs, editing any `--set-secrets` example, and editing ADR 0004.
- A `.specs/` tree.

## Expected behavior

### Scheduler jobs

| Job name | Cron | Timezone | Target |
|----------|------|----------|--------|
| `wine-send-recommendations` | `0 10 * * 4,6` | `America/Sao_Paulo` | `POST {SERVICE_URL}/jobs/send-recommendations` |
| `wine-send-weekly-education` | `0 15 * * 1` | `America/Sao_Paulo` | `POST {SERVICE_URL}/jobs/send-weekly-education` |

Both jobs: location = `REGION` (`southamerica-east1`), headers `X-Job-Internal-Secret=<secret>` and `Content-Type=application/json`, `--max-retry-attempts=3`, `--min-backoff=60s`, `--max-backoff=600s`, `--attempt-deadline=300s`.

### Domain rules

| Constant | Value | Rule |
|----------|-------|------|
| `RECOMMENDATION_WINDOW_GRACE` | `timedelta(hours=6)` | `roll_recommendation_window_if_expired` rolls when `now - start >= ROLLING_RECOMMENDATION_WINDOW - RECOMMENDATION_WINDOW_GRACE` (162h) |
| `RECOMMENDATION_RETRY_GUARD` | `timedelta(hours=24)` | `should_send_scheduled_recommendation` returns False when `last_recommendation_at` is set and `now - last < 24h`, even when count `< 2` |
| `WEEKLY_EDUCATION_GRACE` | `timedelta(hours=6)` | `is_eligible_for_weekly_education` is True when `now - last >= WEEKLY_EDUCATION_COOLDOWN - WEEKLY_EDUCATION_GRACE` (7d − 6h) |

`should_send_scheduled_recommendation` keeps its order: migrate, roll, then the retry guard, then `count < 2`. `is_eligible_for_weekly_education` keeps the active and opt-in checks first; `last is None` stays eligible. Existing tests stay as they are.

### CD step

1. After "Shift traffic to latest revision", the deploy job runs `python3 -m infrastructure.scheduler.apply_scheduler_jobs` with env `PROJECT_ID`, `REGION`, `SERVICE`, `JOB_INTERNAL_SECRET_ID`. No `setup-python`, no `pip install`.
2. The module reads the secret via the runner (`gcloud secrets versions access latest --secret=<JOB_INTERNAL_SECRET_ID>`) and writes `::add-mask::<secret>` as the first stdout line. It reads the service URL via the runner (`gcloud run services describe <SERVICE> --project=<PROJECT_ID> --region=<REGION> --format=value(status.url)`).
3. For each job: `gcloud scheduler jobs describe` → success: `gcloud scheduler jobs update http` with `--update-headers`; failure: `gcloud scheduler jobs create http` with `--headers`.
4. Steps 2–3 are one attempt. Up to 3 attempts; sleep 10s after the first failure and 20s after the second; no sleep after the third. After the third failure the module exits non-zero and the workflow fails.

The module imports the standard library only. The runner (default: `subprocess` running `gcloud`) and the sleep (default: `time.sleep`) are injectable. Argv is never printed.

## Acceptance criteria

One criterion per Expected work ID. Each names the file that proves it.

**EW-01 — Recommendation window grace**
WHEN `should_send_scheduled_recommendation` evaluates a customer whose window started at Thursday 10:00:30 UTC, with `recommendation_send_count_7d == 2` and `last_recommendation_at` older than 24h, at the next Thursday 10:00:00 UTC, THE SYSTEM SHALL roll the window and return True; and WHEN `now = start + 161h59m` with count 2 and the retry guard inactive, THE SYSTEM SHALL not roll and SHALL return False. `RECOMMENDATION_WINDOW_GRACE = timedelta(hours=6)` and the existing 169h roll test still passes.
Test: `tests/unit/domain/test_recommendation_scheduled_cadence.py`.

**EW-02 — Recommendation retry guard**
WHEN `should_send_scheduled_recommendation` evaluates a customer whose `last_recommendation_at` is set and `now - last_recommendation_at < RECOMMENDATION_RETRY_GUARD` (24h), THE SYSTEM SHALL return False even when `recommendation_send_count_7d < 2`: a run 5 minutes after a recorded send skips the customer, and a run 48h later (Saturday slot) still sends.
Test: `tests/unit/domain/test_recommendation_scheduled_cadence.py`.

**EW-03 — Weekly education grace**
WHEN `is_eligible_for_weekly_education` evaluates an active, opted-in customer, THE SYSTEM SHALL return True when `now - last >= WEEKLY_EDUCATION_COOLDOWN - WEEKLY_EDUCATION_GRACE` (`WEEKLY_EDUCATION_GRACE = timedelta(hours=6)`): last Monday 15:00:20 and now the next Monday 15:00:05 is eligible; `now = last + 6d17h59m` is not eligible. Existing tests (3 days ineligible, 7d+1h eligible, naive last 2 days ago ineligible) still pass.
Test: `tests/unit/domain/test_education_eligibility.py`.

**EW-04 — Four-week Thursday/Saturday scenario**
WHEN a customer is driven only through `should_send_scheduled_recommendation` and `record_scheduled_recommendation_send` over eight nominal slots (Thursday and Saturday at 13:00:00 UTC from Thursday 2026-11-12), with run `n` evaluated at `nominal - n * 60s` and a retry at `now + 5 minutes` after every Thursday send, THE SYSTEM SHALL produce exactly 8 sends, one per slot, and no retry SHALL send or record a send.
Test: `tests/unit/domain/test_recommendation_scheduled_cadence.py`.

**EW-05 — Scheduler apply module and job table**
THE SYSTEM SHALL provide `infrastructure/scheduler/__init__.py` (importing nothing) and `infrastructure/scheduler/apply_scheduler_jobs.py`, standard library only, defining exactly the two jobs in the Scheduler jobs table (name, cron, `America/Sao_Paulo`, path, POST) with `--max-retry-attempts=3`, `--min-backoff=60s`, `--max-backoff=600s`, `--attempt-deadline=300s`. No `infrastructure/__init__.py` is added.
Test: `tests/unit/infrastructure/test_apply_scheduler_jobs.py` (job definitions as asserted in the EW-06 argv).

**EW-06 — Create-or-update argv**
WHEN `gcloud scheduler jobs describe` succeeds for a job, THE SYSTEM SHALL run `gcloud scheduler jobs update http` with `--update-headers`; IF `describe` fails, THEN THE SYSTEM SHALL run `gcloud scheduler jobs create http` with `--headers`. Both branches SHALL pass `--location`, `--project`, `--schedule`, `--time-zone`, `--uri` (`{service_url}{path}`), `--http-method=POST`, both headers (`X-Job-Internal-Secret`, `Content-Type=application/json`), and the four retry/deadline flags.
Test: `tests/unit/infrastructure/test_apply_scheduler_jobs.py` (fake runner; both branches × both jobs).

**EW-07 — Secret mask and service URL**
WHEN an attempt starts, THE SYSTEM SHALL read the secret and the service URL through the runner, write `::add-mask::<secret>` as the first stdout line, and write the secret on no other output line; IF the secret or the URL is empty, THEN THE SYSTEM SHALL fail that attempt.
Test: `tests/unit/infrastructure/test_apply_scheduler_jobs.py` (mask line first, secret absent from every other line, empty secret fails, empty URL fails).

**EW-08 — Three CD attempts**
IF an attempt (read secret, read URL, apply both jobs) fails, THEN THE SYSTEM SHALL retry up to 3 attempts total, sleeping 10s after the first failure and 20s after the second, with no sleep after the third: fails twice then succeeds → exit 0 after exactly 3 attempts; fails three times → non-zero exit and no fourth attempt.
Test: `tests/unit/infrastructure/test_apply_scheduler_jobs.py` (fake runner, injected sleep; asserts sleep arguments).

**EW-09 — Deploy workflow step**
THE SYSTEM SHALL declare workflow env `JOB_INTERNAL_SECRET_ID: wine-concierge-job-internal-secret` beside `PROJECT_ID`, `SERVICE`, `REGION`, `IMAGE`, and WHEN "Shift traffic to latest revision" completes, THE SYSTEM SHALL run one step executing `python3 -m infrastructure.scheduler.apply_scheduler_jobs` with `PROJECT_ID`, `REGION`, `SERVICE`, `JOB_INTERNAL_SECRET_ID`; the YAML SHALL contain no secret value, no `set -x`, no `continue-on-error`, no `setup-python`, and no `pip install`, with triggers and earlier steps unchanged.
Verified in: `.github/workflows/deploy.yml` (reviewer diff inspection; no automated test).

**EW-10 — ADR 0005**
THE SYSTEM SHALL include `docs/adrs/0005-cloud-scheduler-from-cd.md` recording: Scheduler provisioned by CD; `X-Job-Internal-Secret` read from Secret Manager at deploy time and written as a static header (no OIDC, no app auth change); prerequisites (Cloud Scheduler API enabled; deploy SA has `roles/cloudscheduler.admin` and `roles/secretmanager.secretAccessor` on the job secret); consequences (anyone who can view the job sees the header; rotation needs a redeploy or `workflow_dispatch`); alternatives (OIDC on the Scheduler target, runbook-only).
Verified in: `docs/adrs/0005-cloud-scheduler-from-cd.md` (reviewer inspection).

**EW-11 — Ops and behavior docs**
THE SYSTEM SHALL update: `docs/DEPLOYMENT.md` with a scheduler section (jobs table, retry flags, ADR 0005 IAM prerequisites, secret ID `wine-concierge-job-internal-secret`, rotation via redeploy or `workflow_dispatch`); `docs/operations/PRODUCTION.md` listing both job names; `docs/operations/SECRET-MANAGER-MIGRATION.md` with exactly three edits (a note that Secret Manager IDs cannot contain `/`, a note that CD reads `wine-concierge-job-internal-secret`, and the deploy-SA sentence changed to state the deploy SA needs `roles/secretmanager.secretAccessor` on that job secret); `docs/specs/entry-recommendation-cadence-sdd.md` with the 6h grace and 24h guard; `docs/specs/weekly-education-job.md` with the 6h grace and the Monday 15:00 `America/Sao_Paulo` schedule; `README.md` Gaps without `Scheduler-from-CD is not done.`; `docs/ROADMAP.md` with "Scheduler created by CD" checked.
Verified in: the listed files (reviewer diff inspection).

**EW-12 — Status flips**
WHILE any of EW-01–EW-11 or EW-13 does not hold, THE SYSTEM SHALL leave status unchanged; once all hold, `docs/ROADMAP-TASKS.md` checks T031, `docs/COMMERCIAL-LAUNCH.md` checks item 27 (`Scheduler in CD`), the SDD status is `implemented`, and the T031 row in `docs/specs/sdd/INDEX.md` matches.
Verified in: the listed files (reviewer diff inspection, ordering confirmed by the builder report).

**EW-13 — Diff and coverage gate**
THE SYSTEM SHALL leave untouched `api/internal_job_auth.py`, Cloud Run deploy flags, `deploy.sh`, `requirements*.txt`, `docs/MVP_SCOPE.md`, on-demand entitlements, `migrate_recommendation_window_from_legacy`, and `send_weekly_education` time handling; and `pytest`, `pytest --cov` (domain/core `fail_under` 95), `ruff check api core domain infrastructure tests`, and `python quality/check_import_style.py` SHALL all pass from the repo root.
Verified by: those four commands, recorded with results in `docs/specs/sdd/T031-builder-report.md`.

## Relevant files

| File | Role |
|------|------|
| `domain/recommendation_scheduled_cadence.py` | Window roll, send decision, record send (EW-01, EW-02) |
| `domain/services/education_eligibility.py` | 7-day cooldown (EW-03) |
| `domain/services/recommendation_service.py` | Job loop; `now_utc` captured once per run. Read only, not changed |
| `api/handlers/jobs_handler.py` | Returns 200 after the loop; an exception yields 500 and Scheduler retries. Read only |
| `infrastructure/scheduler/__init__.py`, `infrastructure/scheduler/apply_scheduler_jobs.py` | New apply module (EW-05–EW-08) |
| `.github/workflows/deploy.yml` | Scheduler step after the traffic shift (EW-09) |
| `tests/unit/domain/test_recommendation_scheduled_cadence.py`, `tests/unit/domain/test_education_eligibility.py` | Domain tests (EW-01–EW-04) |
| `tests/unit/infrastructure/test_apply_scheduler_jobs.py` | Apply-module tests (EW-05–EW-08) |
| `docs/adrs/0005-cloud-scheduler-from-cd.md` | New ADR (EW-10) |
| `docs/DEPLOYMENT.md`, `docs/operations/PRODUCTION.md`, `docs/operations/SECRET-MANAGER-MIGRATION.md` | Ops docs (EW-11) |
| `docs/specs/entry-recommendation-cadence-sdd.md`, `docs/specs/weekly-education-job.md`, `README.md`, `docs/ROADMAP.md` | Behavior docs and status (EW-11) |
| `docs/ROADMAP-TASKS.md`, `docs/COMMERCIAL-LAUNCH.md`, `docs/specs/sdd/T031-scheduler-deploy-cd-sdd.md`, `docs/specs/sdd/INDEX.md` | Status flips (EW-12) |
| `docs/specs/sdd/T031-builder-report.md` | Builder report: one row per EW, Files touched, test commands and results |

## Decisions already made

### User (2026-11-14)

| Topic | Decision |
|-------|----------|
| Recommendations schedule | Thursday and Saturday 10:00 `America/Sao_Paulo`, cron `0 10 * * 4,6` |
| Education schedule | Monday 15:00 `America/Sao_Paulo`, cron `0 15 * * 1` |
| Secret header | Scheduler HTTP target sends `X-Job-Internal-Secret`; CD reads it from Secret Manager at deploy time and writes it as a static header. No app auth change, no OIDC |
| Scheduler retries | `--max-retry-attempts=3` |
| Retry safety | Skip a customer whose `last_recommendation_at` is within the last 24h |
| Window boundary | 6h grace: recommendation window rolls at ≥ 162h; weekly education eligible at ≥ 7d − 6h |
| CD failure | Up to 3 attempts, then the workflow fails (no `continue-on-error`) |

### Orchestrator

| Topic | Decision |
|-------|----------|
| Apply logic location | `infrastructure/scheduler/apply_scheduler_jobs.py`, standard library only, run as `python3 -m infrastructure.scheduler.apply_scheduler_jobs`; no `pip install` in the deploy job |
| GCP calls | `subprocess` running `gcloud`; runner injectable; no live gcloud in tests |
| Secret ID | Workflow env `JOB_INTERNAL_SECRET_ID`, default `wine-concierge-job-internal-secret`. Secret Manager IDs allow only letters, digits, `-`, `_`. Ops must confirm the real ID |
| Scheduler location | Same as `REGION` (`southamerica-east1`) |
| Job names | `wine-send-recommendations`, `wine-send-weekly-education` |
| Backoff | Scheduler `--min-backoff=60s`, `--max-backoff=600s`, `--attempt-deadline=300s`; CD waits 10s then 20s between attempts |
| ADR | New ADR 0005 for provisioning Scheduler from CD with a Secret Manager–sourced header |
| `SECRET-MANAGER-MIGRATION.md` scope (answer to PLAN open question 1) | Change only three things: add the note that IDs cannot contain `/`; state that CD reads `wine-concierge-job-internal-secret`; fix the stale deploy-SA sentence. Leave every other `wine-concierge/...` example, every `--set-secrets` example, and ADR 0004 unchanged |
| Service URL describe flags | `--project=<PROJECT_ID> --region=<REGION> --format=value(status.url)` (PLAN task 7) |
| Package layout | Add only `infrastructure/scheduler/__init__.py`; no `infrastructure/__init__.py` |

## Process constraints

- Imports: one statement per line, no parentheses, no continuation (`python quality/check_import_style.py`).
- Domain must not import infrastructure. The apply module must not import `core.config` or third-party packages.
- Commit bodies wrap at 72 characters. Conventional Commits. Never push to `main`.
- The reviewer reads the SDD, the builder report, and the diff, and does not edit files.
