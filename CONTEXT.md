# CONTEXT — WineAI (wineia)

> Read first. Product milestones: [`docs/ROADMAP.md`](docs/ROADMAP.md). Commercial launch checklist: [`docs/COMMERCIAL-LAUNCH.md`](docs/COMMERCIAL-LAUNCH.md). Micro-tasks: [`docs/ROADMAP-TASKS.md`](docs/ROADMAP-TASKS.md).

## Primary objective (current)

**T010 complete (PR pending):** `JOB_INTERNAL_SECRET` middleware on `/jobs/*` and `/workers/*`.

## Next implementer focus

**T011** — Secret Manager migration plan (COMMERCIAL-LAUNCH #8), or **T012** webhook rate limits (#10), or **T020** tier fields (#17–18).

## Git policy (fixed)

- **No direct commits to `main`** — feature branch + PR only. See [`docs/GIT_WORKFLOW.md`](docs/GIT_WORKFLOW.md).

## Job/worker auth (implemented)

| Item | Value |
|------|--------|
| Env | `JOB_INTERNAL_SECRET` in `core/config.py` |
| Header | `X-Job-Internal-Secret` |
| Enforcement | `api/internal_job_auth.py` + `api/routes.py` |
| Cloud Tasks | `infrastructure/queue/cloud_tasks_client.py` adds header when secret set |
| Docs | [DEPLOYMENT.md](docs/DEPLOYMENT.md), [PRODUCTION.md](docs/operations/PRODUCTION.md) |

**Ops action after deploy:** set `JOB_INTERNAL_SECRET` on Cloud Run and configure Cloud Scheduler job targets with the same header.

## Product decisions (commercial — owner confirmed)

| Code | Offering |
|------|-----------|
| `ENTRY` | Recommendation messages **2× per week** |
| `SUPERIOR` | Entry + on-demand AI in WhatsApp |
| `weekly_education_opt_in` | Optional **1 didactic message / week** |

## Agent handoff

On-call: [`.cursor/agents/on-call.md`](.cursor/agents/on-call.md).
