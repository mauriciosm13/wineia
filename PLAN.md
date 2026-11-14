# PLAN — T031 Scheduler jobs in deploy/CD

Source of truth: `CONTEXT.md`, Expected work EW-01–EW-13 in `docs/specs/sdd/T031-scheduler-deploy-cd-sdd.md`, and the recon summary. Branch `feat/t031-scheduler-cd` already exists. No commit and no push.

Do not add behavior the Expected work list does not name. Out of scope stays out: `api/internal_job_auth.py`, Cloud Run deploy flags, `--set-secrets`, `deploy.sh`, `/workers/*`, campaign producer, `migrate_recommendation_window_from_legacy`, how `send_weekly_education` stamps or reads time, new pip dependencies, `docs/MVP_SCOPE.md`, on-demand entitlements, and creating IAM bindings or enabling APIs.

`PLAN.md` is this handoff. It is not an Expected work product. Do not treat it as a T031 deliverable in the builder report.

## Order

| # | Task | EW | Depends on |
|---|------|----|------------|
| 1 | Recommendation window grace | EW-01 | — |
| 2 | Recommendation retry guard | EW-02 | 1 |
| 3 | Weekly education grace | EW-03 | — |
| 4 | Four-week Thursday/Saturday scenario | EW-04 | 1, 2 |
| 5 | Scheduler apply module and job table | EW-05 | — |
| 6 | Create-or-update argv | EW-06 | 5 |
| 7 | Secret mask and service URL | EW-07 | 5 |
| 8 | Three CD attempts | EW-08 | 6, 7 |
| 9 | Deploy workflow step | EW-09 | 8 |
| 10 | ADR 0005 | EW-10 | 9 |
| 11 | Ops and behavior docs | EW-11 | 9 |
| 12 | Diff and coverage gate | EW-13 | 1–11 |
| 13 | Status flips | EW-12 | 12 |
| 14 | Builder report | EW-01–EW-13 | 13 |

Tasks 1–4 are the domain slice (tests with the code). Tasks 5–8 are the infrastructure slice (tests with the code). Task 3 does not depend on 1–2; it stays in the domain slice and lands before the scenario only so domain work finishes together. Task 11 does not depend on task 10; both wait until the workflow step exists.

## Tasks

### 1. Recommendation window grace (EW-01)

Files: `domain/recommendation_scheduled_cadence.py`, `tests/unit/domain/test_recommendation_scheduled_cadence.py`.

- Add `RECOMMENDATION_WINDOW_GRACE = timedelta(hours=6)`.
- `roll_recommendation_window_if_expired` rolls when `now_utc - start >= ROLLING_RECOMMENDATION_WINDOW - RECOMMENDATION_WINDOW_GRACE` (162h). Leave `migrate_recommendation_window_from_legacy` unchanged. It still compares against the full 168h.
- Keep the existing roll test (`169h` still rolls). Recon: no current domain test breaks on the 6h grace.
- New test: window start Thursday 10:00:30 UTC, `recommendation_send_count_7d == 2`, `last_recommendation_at` older than 24h, `now` the next Thursday 10:00:00 UTC. The window rolls and `should_send_scheduled_recommendation` returns True. The guard from task 2 is why `last_recommendation_at` must be older than 24h; without that, the send assertion fails after EW-02.
- New test: `now = start + 161h59m`, count 2, guard inactive (no `last_recommendation_at`, or one older than 24h). No roll. Send is denied because the count stays 2.

### 2. Recommendation retry guard (EW-02)

Same files as task 1.

- Add `RECOMMENDATION_RETRY_GUARD = timedelta(hours=24)`.
- `should_send_scheduled_recommendation` keeps the current order: migrate, then roll, then the count check. After roll, return False when `last_recommendation_at` is set and `now - last < RECOMMENDATION_RETRY_GUARD`, even when the count is still `< 2`. Otherwise return `count < 2`.
- `record_scheduled_recommendation_send` already sets `last_recommendation_at`. Do not change it. `send_recommendations` already captures `now_utc` once per run. Do not change `domain/services/recommendation_service.py`.
- Test: a run 5 minutes after a recorded send skips the customer while the count is still `< 2`.
- Test: a run 48h later (Saturday slot) still sends.
- Imports stay one statement per line, no parentheses.

### 3. Weekly education grace (EW-03)

Files: `domain/services/education_eligibility.py`, `tests/unit/domain/test_education_eligibility.py`.

- Add `WEEKLY_EDUCATION_GRACE = timedelta(hours=6)`.
- `is_eligible_for_weekly_education` is True when `now - last >= WEEKLY_EDUCATION_COOLDOWN - WEEKLY_EDUCATION_GRACE`, after the existing active and opt-in checks. `last is None` stays eligible.
- Do not change `send_weekly_education`. It passes no `now` and stamps naive `utcnow` after the Claude call.
- Existing tests stay as they are (3 days still ineligible, 7d+1h still eligible, naive last 2 days ago still ineligible).
- New test, using the existing `_customer` helper: `last` Monday 15:00:20, `now` the next Monday 15:00:05 → eligible.
- New test: `now = last + 6d17h59m` → not eligible.

### 4. Four-week Thursday/Saturday scenario (EW-04)

File: `tests/unit/domain/test_recommendation_scheduled_cadence.py`.

Drive the scenario only through `should_send_scheduled_recommendation` and `record_scheduled_recommendation_send`. Do not call the job service.

- Eight nominal slots over four weeks: Thursday and Saturday at 13:00:00 UTC (10:00 America/Sao_Paulo). Anchor the first Thursday on a real Thursday (2026-11-12 13:00:00 UTC).
- Run `n` (0-based, in slot order) is evaluated at `nominal - n * 60s`, so each later run starts 60s earlier than the previous run. That is the EW-04 bound (60s), still inside the 6h grace.
- After every Thursday send, evaluate again at that run's `now + 5 minutes`. That retry must not send and must not call `record_scheduled_recommendation_send`.
- The customer gets exactly 8 sends, one per scheduled slot.

### 5. Scheduler apply module and job table (EW-05)

Files: `infrastructure/scheduler/__init__.py`, `infrastructure/scheduler/apply_scheduler_jobs.py`.

- `infrastructure/` has no `__init__.py` (namespace packages). Add only `infrastructure/scheduler/__init__.py`. Do not add `infrastructure/__init__.py`. The scheduler `__init__.py` imports nothing.
- The apply module imports the standard library only. No `core.config`, no third-party packages.
- Define exactly two jobs:

| Name | Cron | Timezone | Path | Method |
|------|------|----------|------|--------|
| `wine-send-recommendations` | `0 10 * * 4,6` | `America/Sao_Paulo` | `/jobs/send-recommendations` | POST |
| `wine-send-weekly-education` | `0 15 * * 1` | `America/Sao_Paulo` | `/jobs/send-weekly-education` | POST |

- Retry flags on both: `--max-retry-attempts=3`, `--min-backoff=60s`, `--max-backoff=600s`, `--attempt-deadline=300s`.
- Location is `REGION`. The entrypoint is `python3 -m infrastructure.scheduler.apply_scheduler_jobs`.

### 6. Create-or-update argv (EW-06)

Files: the apply module and `tests/unit/infrastructure/test_apply_scheduler_jobs.py`. `tests/unit/infrastructure/` already exists.

- The runner is injectable. The default runner uses `subprocess` to run `gcloud`. Tests pass a fake runner. No live gcloud.
- For each job: `describe`. Success → `gcloud scheduler jobs update http` with `--update-headers`. Failure → `gcloud scheduler jobs create http` with `--headers`.
- Both branches pass `--location`, `--project`, `--schedule`, `--time-zone`, `--uri` (`{service_url}{path}`), `--http-method=POST`, both headers (`X-Job-Internal-Secret` and `Content-Type=application/json`), and the four retry/deadline flags.
- Tests assert that argv for both branches and both jobs.

### 7. Secret mask and service URL (EW-07)

Same files as task 6.

- Read the secret with the runner: `gcloud secrets versions access latest --secret=<JOB_INTERNAL_SECRET_ID>`.
- Read the URL with the runner: `gcloud run services describe <SERVICE> --project=<PROJECT_ID> --region=<REGION> --format=value(status.url)`. The Behavior section names this describe; `--project` and `--region` select the service the rest of `deploy.yml` already deploys, using env the step already has.
- The first line written to stdout is `::add-mask::<secret>`, before any other output. No other output line contains the secret. Do not print argv.
- An empty secret or an empty URL fails that attempt.
- Tests assert all three: mask line, secret absent from every other line, empty secret and empty URL each fail the attempt.

### 8. Three CD attempts (EW-08)

Same files as task 6.

- One attempt is read secret, then read URL, then apply both jobs.
- Up to 3 attempts. Sleep between them is injectable (default `time.sleep`): 10s after the first failure, 20s after the second. No sleep after the third failure.
- Fails twice then succeeds → exit 0 and exactly 3 attempts.
- Fails three times → non-zero exit and no fourth attempt.
- Tests assert both outcomes, including the sleep arguments.

### 9. Deploy workflow step (EW-09)

File: `.github/workflows/deploy.yml`.

- Add workflow env `JOB_INTERNAL_SECRET_ID: wine-concierge-job-internal-secret` next to `PROJECT_ID`, `SERVICE`, `REGION`, and `IMAGE`.
- Add one step after `Shift traffic to latest revision` (that step stays last today). It runs `python3 -m infrastructure.scheduler.apply_scheduler_jobs` with env `PROJECT_ID`, `REGION`, `SERVICE`, and `JOB_INTERNAL_SECRET_ID`.
- The deploy job has no `setup-python`; `ubuntu-latest` `python3` is enough. Do not add a Python setup step. Do not `pip install`.
- No secret value in the YAML, no `set -x`, no `continue-on-error`. Triggers unchanged. Earlier steps unchanged, including Cloud Run flags.

### 10. ADR 0005 (EW-10)

File: `docs/adrs/0005-cloud-scheduler-from-cd.md`. Next free number after ADR 0004.

Record:

- Cloud Scheduler jobs are provisioned by CD.
- The `X-Job-Internal-Secret` header is read from Secret Manager at deploy time and written as a static header. No OIDC. No app auth change.
- Prerequisites: Cloud Scheduler API enabled; deploy service account has `roles/cloudscheduler.admin` and `roles/secretmanager.secretAccessor` on the job secret. Document only. Do not create the bindings.
- Consequences: anyone who can view the job sees the header; rotating the secret needs a redeploy or `workflow_dispatch`.
- Alternatives considered: OIDC on the Scheduler target, and a runbook-only setup.

### 11. Ops and behavior docs (EW-11)

Update only these facts:

- `docs/DEPLOYMENT.md`: scheduler section with the jobs table (names, crons, timezone, paths), retry flags, IAM prerequisites from ADR 0005, secret id `wine-concierge-job-internal-secret`, and rotation via redeploy or `workflow_dispatch`.
- `docs/operations/PRODUCTION.md`: list both job names.
- `docs/operations/SECRET-MANAGER-MIGRATION.md`: note that Secret Manager ids cannot contain `/`; note that CD reads `wine-concierge-job-internal-secret`; change the deploy-SA sentence (~line 81) so it no longer says the deploy SA needs no Secret Manager access. State that the deploy SA needs `roles/secretmanager.secretAccessor` on that job secret. See the open question before rewriting any other `wine-concierge/...` id or any `--set-secrets` example.
- `docs/specs/entry-recommendation-cadence-sdd.md`: document the 6h grace and the 24h guard.
- `docs/specs/weekly-education-job.md`: document the 6h grace and the Monday 15:00 `America/Sao_Paulo` schedule.
- `README.md` Gaps: remove the line `Scheduler-from-CD is not done.`
- `docs/ROADMAP.md`: check `Scheduler created by CD`.

### 12. Diff and coverage gate (EW-13)

Run this after tasks 1–11 and before any status flip.

- The diff does not touch `api/internal_job_auth.py`, Cloud Run deploy flags, `deploy.sh`, `requirements*.txt`, `docs/MVP_SCOPE.md`, on-demand entitlements, or `migrate_recommendation_window_from_legacy`. It also does not change `send_weekly_education` time handling.
- Commands, from the repo root:
  - `pytest`
  - `pytest --cov` (sources `domain` and `core`, `fail_under` 95). Infrastructure is linted and collected; it is not a coverage source.
  - `ruff check api core domain infrastructure tests`
  - `python quality/check_import_style.py`
- All four pass, and domain/core coverage stays ≥ 95%. Record the exact commands and results for the builder report.

### 13. Status flips (EW-12)

Only after tasks 1–12 hold:

- `docs/ROADMAP-TASKS.md`: check T031.
- `docs/COMMERCIAL-LAUNCH.md`: check item 27 (`Scheduler in CD`).
- `docs/specs/sdd/T031-scheduler-deploy-cd-sdd.md`: status `implemented`.
- `docs/specs/sdd/INDEX.md`: T031 row matches `implemented`.

### 14. Builder report

File: `docs/specs/sdd/T031-builder-report.md`.

One row per EW-01–EW-13: result `done` or `skipped`, files, what changed. Then a **Files touched** list of every path in the diff, plus the exact test commands and results from task 12. Any path not justified by an EW id is extra. Do not edit the report from the reviewer side.

## Open questions

1. `docs/operations/SECRET-MANAGER-MIGRATION.md` uses `wine-concierge/<slug>` for Twilio, Anthropic, WhatsApp, and `wine-concierge/job-internal-secret`, including `--set-secrets` examples. EW-11 requires three edits: ids cannot contain `/`, CD reads `wine-concierge-job-internal-secret`, and the deploy-SA sentence no longer says the deploy SA needs no Secret Manager access. No replacement ids are decided for the other secrets, and `--set-secrets` changes are out of scope. Task 11 follows those three sentences and leaves the other slash ids in place beside the new note. Confirm that this is the intended fix. Renaming the other ids needs the real ids from ops before anyone rewrites the examples.
