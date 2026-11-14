# CONTEXT — WineAI (wineia)

> Read first. Product milestones: [`docs/ROADMAP.md`](docs/ROADMAP.md). Commercial launch checklist: [`docs/COMMERCIAL-LAUNCH.md`](docs/COMMERCIAL-LAUNCH.md). Micro-tasks: [`docs/ROADMAP-TASKS.md`](docs/ROADMAP-TASKS.md).

## Primary objective (current)

**T031** — The deploy workflow creates or updates the Cloud Scheduler jobs that call `POST /jobs/send-recommendations` and `POST /jobs/send-weekly-education`. Customers must not lose a scheduled message because of window boundaries or retries.

The comparison contract is [`docs/specs/sdd/T031-scheduler-deploy-cd-sdd.md`](docs/specs/sdd/T031-scheduler-deploy-cd-sdd.md). Its **Expected work** list (EW-01–EW-13) is what the reviewer checks against the builder report. Do not add behavior that list does not name.

## Decisions already made (user, 2026-11-14)

| Topic | Decision |
|-------|----------|
| Recommendations schedule | Thursday and Saturday at 10:00, `America/Sao_Paulo` — cron `0 10 * * 4,6` |
| Education schedule | Monday at 15:00, `America/Sao_Paulo` — cron `0 15 * * 1` |
| Secret header | Cloud Scheduler HTTP target sends `X-Job-Internal-Secret`. The CD reads the value from Secret Manager at deploy time and writes it as a static header. No app auth change. No OIDC. |
| Scheduler retries | At most 3 retries per run (`--max-retry-attempts=3`). |
| Retry safety | The recommendation job skips a customer whose `last_recommendation_at` is within the last 24h, so a retried run never sends twice. |
| Window boundary | 6h grace: the 168h recommendation window rolls at ≥ 162h; weekly education is eligible at ≥ 7 days − 6h. |
| CD failure | The scheduler step tries up to 3 attempts. If all fail, the workflow fails (no `continue-on-error`). |

## Decisions made by the orchestrator

| Topic | Decision |
|-------|----------|
| Where the apply logic lives | `infrastructure/scheduler/apply_scheduler_jobs.py`, standard library only, run as `python3 -m infrastructure.scheduler.apply_scheduler_jobs`. The deploy job does not `pip install`. |
| How it calls GCP | `subprocess` running `gcloud`. The runner function is injectable so unit tests use a fake. No live gcloud in tests. |
| Secret ID | Workflow env `JOB_INTERNAL_SECRET_ID`, default `wine-concierge-job-internal-secret`. Secret Manager IDs only allow letters, digits, `-`, and `_`; the `wine-concierge/...` names in the runbook are not valid IDs. Ops must confirm the real ID. |
| Scheduler location | Same as `REGION` (`southamerica-east1`). |
| Job names | `wine-send-recommendations`, `wine-send-weekly-education`. |
| Backoff | Scheduler: `--min-backoff=60s`, `--max-backoff=600s`, `--attempt-deadline=300s`. CD attempts: wait 10s then 20s between attempts. |
| ADR | New ADR 0005 for provisioning Cloud Scheduler from CD with a Secret Manager–sourced header. |

## Out of scope

- OIDC tokens on Scheduler or any change to `api/internal_job_auth.py`.
- Changing Cloud Run deploy flags, `--set-secrets`, or `deploy.sh`.
- Scheduling `/workers/*` or a campaign producer.
- On-demand entitlements (T024/T060/T061), async webhook replies (T032).
- `migrate_recommendation_window_from_legacy` behavior.
- New pip dependencies.
- `docs/MVP_SCOPE.md`.
- Reordering enqueue vs Datastore update in job loops (residual duplicate risk on partial failure; track separately).
- Changing how `send_weekly_education` stamps or reads time.
- Creating GCP IAM bindings or enabling APIs. Those are documented ops prerequisites, not code.

## Relevant files

| File | Role |
|------|------|
| `domain/recommendation_scheduled_cadence.py` | Window roll, send decision, record send |
| `domain/services/education_eligibility.py` | 7-day cooldown |
| `domain/services/recommendation_service.py` | Job loop; `now_utc` captured once per run |
| `api/handlers/jobs_handler.py` | Returns 200 after the loop; an exception yields 500 and Scheduler retries |
| `.github/workflows/deploy.yml` | Add the scheduler step after the traffic shift |
| `infrastructure/scheduler/` | New apply module |
| `tests/unit/domain/test_recommendation_scheduled_cadence.py`, `tests/unit/domain/test_education_eligibility.py` | Domain tests |
| `tests/unit/infrastructure/` | Apply-module tests |
| `docs/DEPLOYMENT.md`, `docs/operations/PRODUCTION.md`, `docs/operations/SECRET-MANAGER-MIGRATION.md` | Ops docs |
| `docs/specs/entry-recommendation-cadence-sdd.md`, `docs/specs/weekly-education-job.md` | Behavior specs to update |

## Acceptance criteria

See EW-01–EW-13 in the SDD. In short:

- [ ] Domain grace and 24h guard, with boundary tests and a 4-week Thursday/Saturday scenario.
- [ ] Idempotent create-or-update of exactly two Scheduler jobs with the schedules, timezone, header, and retry flags above.
- [ ] Secret is masked and never printed; up to 3 CD attempts, then fail.
- [ ] `deploy.yml` runs the module after the traffic shift.
- [ ] ADR 0005 and ops docs; T031, CL #27, SDD index updated last.
- [ ] pytest, ruff, `python quality/check_import_style.py` pass. Domain/core coverage ≥ 95%.

## Git policy (fixed)

Branch: `feat/t031-scheduler-cd` from `main`. See [`docs/GIT_WORKFLOW.md`](docs/GIT_WORKFLOW.md). **Never push to `main`.** Do not commit or push until the orchestrator asks. Commit bodies wrap at 72 characters (commitlint `body-max-line-length` is 100).

## Agent handoff

On-call: [`.cursor/agents/on-call.md`](.cursor/agents/on-call.md).

Builder report path: `docs/specs/sdd/T031-builder-report.md` (one row per Expected work ID, files, done or skipped, plus Files touched). The reviewer reads that file, the SDD, and the diff, and is the judge. The reviewer does not edit any file.
