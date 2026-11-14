# Builder report — T031 Scheduler jobs in deploy/CD

**SDD:** [T031-scheduler-deploy-cd-sdd.md](./T031-scheduler-deploy-cd-sdd.md)  
**Branch:** `feat/t031-scheduler-cd` (uncommitted; the orchestrator commits)  
**Date:** 2026-11-14

## Expected work

| ID | Result | Files | What changed |
|----|--------|-------|--------------|
| EW-01 | done | `domain/recommendation_scheduled_cadence.py`, `tests/unit/domain/test_recommendation_scheduled_cadence.py` | Added `RECOMMENDATION_WINDOW_GRACE = timedelta(hours=6)`. `roll_recommendation_window_if_expired` rolls at `now - start >= ROLLING_RECOMMENDATION_WINDOW - RECOMMENDATION_WINDOW_GRACE`. Tests: start Thu 2026-11-12 10:00:30 UTC, count 2, last send 48h after start, now Thu 2026-11-19 10:00:00 → rolls and send allowed; `now = start + 161h59m` → no roll, send denied. Existing 169h roll test unchanged. `migrate_recommendation_window_from_legacy` unchanged (still full 168h). |
| EW-02 | done | same | Added `RECOMMENDATION_RETRY_GUARD = timedelta(hours=24)`. `should_send_scheduled_recommendation` keeps migrate → roll, then returns False when `_as_utc(last_recommendation_at)` is set and `now - last < 24h`, then `count < 2`. Tests: run 5 min after a recorded send skips (count still 1); run 48h later sends; naive `last_recommendation_at` is normalized. |
| EW-03 | done | `domain/services/education_eligibility.py`, `tests/unit/domain/test_education_eligibility.py` | Added `WEEKLY_EDUCATION_GRACE = timedelta(hours=6)`; eligible when `now - last >= WEEKLY_EDUCATION_COOLDOWN - WEEKLY_EDUCATION_GRACE`. Active/opt-in checks and `last is None` unchanged. Tests: last Mon 2026-11-09 15:00:20, now Mon 2026-11-16 15:00:05 → eligible; `last + 6d17h59m` → not eligible. Existing tests unchanged. `send_weekly_education` unchanged. |
| EW-04 | done | `tests/unit/domain/test_recommendation_scheduled_cadence.py` | `test_four_weeks_thursday_saturday_runs_send_once_per_slot`: 8 slots (Thu/Sat 13:00 UTC from Thu 2026-11-12), run `n` at `nominal - n * 60s`, retry at `now + 5 min` after every Thursday send must return False and is never recorded. Asserts exactly 8 sends, one per slot. Uses only `should_send_scheduled_recommendation` and `record_scheduled_recommendation_send`. |
| EW-05 | done | `infrastructure/scheduler/__init__.py`, `infrastructure/scheduler/apply_scheduler_jobs.py` | Empty package `__init__.py` (no `infrastructure/__init__.py`). Module imports only `os`, `subprocess`, `sys`, `time`. `JOBS` defines exactly `wine-send-recommendations` (`0 10 * * 4,6`, `/jobs/send-recommendations`) and `wine-send-weekly-education` (`0 15 * * 1`, `/jobs/send-weekly-education`), `America/Sao_Paulo`, POST, retry flags `--max-retry-attempts=3 --min-backoff=60s --max-backoff=600s --attempt-deadline=300s`. |
| EW-06 | done | module, `tests/unit/infrastructure/test_apply_scheduler_jobs.py` | Per job: `gcloud scheduler jobs describe <name> --location --project --format=value(name)`; success → `jobs update http ... --update-headers=X-Job-Internal-Secret=<secret>,Content-Type=application/json`; failure → `jobs create http ... --headers=...`. Both pass `--location`, `--project`, `--schedule`, `--time-zone`, `--uri={service_url}{path}`, `--http-method=POST`, and the four retry flags; no body flag. Tests assert full argv for create × both jobs, update × both jobs, and mixed. |
| EW-07 | done | same | Secret via runner (`gcloud secrets versions access latest --secret=<JOB_INTERNAL_SECRET_ID> --project=<PROJECT_ID>`); URL via runner (`gcloud run services describe <SERVICE> --project --region --format=value(status.url)`). First stdout line is `::add-mask::<secret>` (masked once per distinct value). Failure messages go to stderr and never contain the secret; argv is never printed. Empty (or whitespace-only) secret and empty URL fail the attempt. Tests: mask first, secret absent from every other stdout line and from stderr (success and all-fail paths), empty secret fails, empty URL fails. |
| EW-08 | done | same | `apply_with_retries`: up to 3 attempts, injected `sleep(10)` after the first failure and `sleep(20)` after the second, none after the third. Tests: fails twice then succeeds → exit 0, 3 secret reads, sleeps `[10, 20]`; fails three times → non-zero, 3 secret reads (no fourth), sleeps `[10, 20]`. Missing env → exit 2, no gcloud call. `main()` returns the exit code; `__main__` calls `sys.exit(main())`. |
| EW-09 | done | `.github/workflows/deploy.yml` | Added workflow env `JOB_INTERNAL_SECRET_ID: wine-concierge-job-internal-secret` and a final step **Apply Cloud Scheduler jobs** after **Shift traffic to latest revision**, running `python3 -m infrastructure.scheduler.apply_scheduler_jobs` with env `PROJECT_ID`, `REGION`, `SERVICE`, `JOB_INTERNAL_SECRET_ID`. Additions only (9 lines); no secret value, no `set -x`, no `continue-on-error`, no `setup-python`, no `pip install`; triggers and earlier steps unchanged. |
| EW-10 | done | `docs/adrs/0005-cloud-scheduler-from-cd.md` | New ADR in ADR 0004 style: Scheduler provisioned by CD; header read from Secret Manager at deploy time as a static header (no OIDC, no app auth change); prerequisites (Cloud Scheduler API, `roles/cloudscheduler.admin`, `roles/secretmanager.secretAccessor` on the job secret); consequences (job viewers see the header; rotation needs redeploy or `workflow_dispatch`); alternatives (OIDC, runbook-only). |
| EW-11 | done | `docs/DEPLOYMENT.md`, `docs/operations/PRODUCTION.md`, `docs/operations/SECRET-MANAGER-MIGRATION.md`, `docs/specs/entry-recommendation-cadence-sdd.md`, `docs/specs/weekly-education-job.md`, `README.md`, `docs/ROADMAP.md` | DEPLOYMENT: new section "Cloud Scheduler jobs (created by CD)" (jobs table, retries, IAM prerequisites, secret ID, rotation, CD failure), step 5 in the CI/CD step list, stale "not yet created by CD" bullet and stale Scheduler header paragraph now point to the section. PRODUCTION: "Cloud Scheduler jobs" table with both names. SECRET-MANAGER-MIGRATION: exactly three edits — note that IDs cannot contain `/`, note that CD reads `wine-concierge-job-internal-secret`, deploy-SA sentence now requires `secretAccessor` on that secret; other slash IDs and `--set-secrets` examples untouched. Cadence SDD: 6h grace + 24h guard section and revision row. Weekly education spec: 6h grace and Monday 15:00 `America/Sao_Paulo` schedule. README Gaps line removed. ROADMAP "Scheduler created by CD" checked. |
| EW-12 | done | `docs/ROADMAP-TASKS.md`, `docs/COMMERCIAL-LAUNCH.md`, `docs/specs/sdd/T031-scheduler-deploy-cd-sdd.md`, `docs/specs/sdd/INDEX.md` | Flipped only after EW-01–EW-11 and the EW-13 gate passed: T031 checked, item 27 checked, SDD status `implemented`, INDEX row `implemented`. |
| EW-13 | done | whole diff | `git diff --name-only` contains none of `api/internal_job_auth.py`, `deploy.sh`, `requirements*.txt`, `docs/MVP_SCOPE.md`, on-demand entitlements, `domain/services/recommendation_service.py`, `domain/services/education_service.py`; `migrate_recommendation_window_from_legacy` body unchanged; Cloud Run deploy flags unchanged. Gate commands below all pass; domain/core coverage 95.48%. |

## Deviations from the SDD / SPEC

1. Secret read argv adds `--project=<PROJECT_ID>` beyond the SPEC's `--secret=<ID>`, so the secret is read from the deploy project even if the gcloud default project differs.
2. `gcloud scheduler jobs describe` passes `--location`, `--project`, and `--format=value(name)` (the SPEC names only `describe`); `--format` keeps the existing job's header value out of captured output.
3. Exit codes: missing env → 2; all three attempts failed → 1. Failure messages go to stderr; stdout carries only the mask line and `created|updated scheduler job <name>` lines.

## Files touched

Handoff files (pre-existing uncommitted, not T031 deliverables): `CONTEXT.md`, `PLAN.md`, `SPEC.md`.

| Path | EW |
|------|----|
| `domain/recommendation_scheduled_cadence.py` | EW-01, EW-02 |
| `domain/services/education_eligibility.py` | EW-03 |
| `tests/unit/domain/test_recommendation_scheduled_cadence.py` | EW-01, EW-02, EW-04 |
| `tests/unit/domain/test_education_eligibility.py` | EW-03 |
| `infrastructure/scheduler/__init__.py` (new) | EW-05 |
| `infrastructure/scheduler/apply_scheduler_jobs.py` (new) | EW-05–EW-08 |
| `tests/unit/infrastructure/test_apply_scheduler_jobs.py` (new) | EW-05–EW-08 |
| `.github/workflows/deploy.yml` | EW-09 |
| `docs/adrs/0005-cloud-scheduler-from-cd.md` (new) | EW-10 |
| `docs/DEPLOYMENT.md` | EW-11 |
| `docs/operations/PRODUCTION.md` | EW-11 |
| `docs/operations/SECRET-MANAGER-MIGRATION.md` | EW-11 |
| `docs/specs/entry-recommendation-cadence-sdd.md` | EW-11 |
| `docs/specs/weekly-education-job.md` | EW-11 |
| `README.md` | EW-11 |
| `docs/ROADMAP.md` | EW-11 |
| `docs/ROADMAP-TASKS.md` | EW-12 |
| `docs/COMMERCIAL-LAUNCH.md` | EW-12 |
| `docs/specs/sdd/T031-scheduler-deploy-cd-sdd.md` | EW-12 (status; the rest of its diff is the orchestrator's handoff) |
| `docs/specs/sdd/INDEX.md` | EW-12 |
| `docs/specs/sdd/T031-builder-report.md` (new) | this report |

## Test commands and results

Run from the repo root with the repo virtualenv (`.venv`), before the EW-12 flips:

| Command | Result |
|---------|--------|
| `PYTHONPATH=. .venv/bin/python -m pytest` | 187 passed |
| `PYTHONPATH=. .venv/bin/python -m pytest --cov --cov-report=term-missing` | 187 passed; total coverage 95.48% (`fail_under` 95 reached); `domain/recommendation_scheduled_cadence.py` and `domain/services/education_eligibility.py` 100% |
| `.venv/bin/ruff check api core domain infrastructure tests quality` | All checks passed |
| `.venv/bin/python quality/check_import_style.py` | Import style OK |
| `python3 -m py_compile infrastructure/scheduler/apply_scheduler_jobs.py` | OK |
| `env -i PATH=/usr/bin:/bin python3 -m infrastructure.scheduler.apply_scheduler_jobs` | exit 2, `missing required env: PROJECT_ID, REGION, SERVICE, JOB_INTERNAL_SECRET_ID`, no traceback |
| `env -i PATH=/usr/bin:/bin PROJECT_ID=p REGION=r SERVICE=s JOB_INTERNAL_SECRET_ID=x python3 -m infrastructure.scheduler.apply_scheduler_jobs` (no gcloud on PATH) | exit 1 after 3 attempts (`could not read secret x (exit 127)`), no traceback |
