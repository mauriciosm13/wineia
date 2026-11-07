# CONTEXT — WineAI (wineia)

> Read first. Product milestones: [`docs/ROADMAP.md`](docs/ROADMAP.md). Commercial launch checklist: [`docs/COMMERCIAL-LAUNCH.md`](docs/COMMERCIAL-LAUNCH.md). Micro-tasks: [`docs/ROADMAP-TASKS.md`](docs/ROADMAP-TASKS.md).

## Primary objective (current)

**T022** — Weekly education job: `POST /jobs/send-weekly-education` with `JOB_INTERNAL_SECRET`, opt-in cohort, rolling 7-day cadence, one shared Claude copy per run, Cloud Tasks fan-out. Maps to COMMERCIAL-LAUNCH #25 and [`docs/commercial.md`](docs/commercial.md).

**T021** is merged on `main` — see [`entry-recommendation-cadence-sdd.md`](docs/specs/entry-recommendation-cadence-sdd.md).

## Acceptance criteria (T022)

- [x] Job route follows `/jobs/send-recommendations` auth pattern.
- [x] Cohort: **active** customers with `weekly_education_opt_in == true`.
- [x] At most 1 education send per customer per **rolling 7 days** (`last_weekly_education_at`).
- [x] One `generate_weekly_education()` Claude call per job run; same body enqueued per eligible phone.
- [x] Portuguese copy; logic in `domain/`; thin HTTP handler.
- [x] Unit tests: opt-in filter, cadence skip/send.
- [x] Lite spec `docs/specs/weekly-education-job.md`; PRODUCTION.md; T022 + CL #25 marked done.
- [x] pytest, ruff, import style pass.

## Decisions (T022)

| Topic | Decision |
|-------|----------|
| Cadence | Rolling **7×24h** from `last_weekly_education_at` (not ISO calendar week) |
| Cadence field | `last_weekly_education_at` on customer entity (set on send) |
| Shared copy | Single `IAService.generate_weekly_education()` per job invocation |

## Relevant files

| File | Action |
|------|--------|
| `domain/services/education_service.py` | Job orchestration |
| `domain/services/education_eligibility.py` | Pure eligibility |
| `domain/services/ia_service.py` | `generate_weekly_education` |
| `api/handlers/jobs_handler.py` | HTTP handler |
| `api/routes.py` | Route registration |
| `docs/specs/weekly-education-job.md` | Lite spec |
| `tests/unit/domain/test_education_eligibility.py` | Unit tests |
| `tests/unit/domain/test_education_service.py` | Unit tests |

## Git policy (fixed)

- Use readable branch names; avoid random suffixes. If automation requires `cursor/`, use `cursor/<type>-<topic-kebab>`. See [`docs/GIT_WORKFLOW.md`](docs/GIT_WORKFLOW.md#branch-names-preferred).

## Next after T022

**T023** one Claude call per recommendation broadcast slot, or **T024** domain entitlements.

## Agent handoff

On-call: [`.cursor/agents/on-call.md`](.cursor/agents/on-call.md).
