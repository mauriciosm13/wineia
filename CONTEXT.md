# CONTEXT — WineAI (wineia)

> Read first. Product milestones: [`docs/ROADMAP.md`](docs/ROADMAP.md). Commercial launch checklist: [`docs/COMMERCIAL-LAUNCH.md`](docs/COMMERCIAL-LAUNCH.md). Micro-tasks: [`docs/ROADMAP-TASKS.md`](docs/ROADMAP-TASKS.md).

## Primary objective (current)

**T024** — Domain + Datastore **on-demand** entitlements for webhook IA (`messaging_service`), tier-based daily caps, read-path daily reset. Separate from T012 abuse limits and T021 scheduled cadence.

## Acceptance criteria (T024)

- [x] Replace hardcoded `DAILY_LIMIT` with `plan_tier` limits (ENTRY 2, SUPERIOR 10 — MVP defaults).
- [x] `messages_sent_today` + `daily_reset` UTC read-path reset documented.
- [x] Recommendation / education jobs unchanged.
- [x] Lite spec `docs/specs/on-demand-entitlements-sdd.md`; PRODUCTION; T024 + CL #18a.
- [x] Unit tests: `on_demand_entitlements` + `messaging_service` tier/reset paths.
- [x] pytest, ruff, import style; domain/core coverage ≥ 95%.

## Decisions (T024)

| Topic | Decision |
|-------|----------|
| Limits | `domain/on_demand_entitlements.py` constants; T060 may add config/ops tuning |
| Reset | Compare `daily_reset` to UTC calendar day on inbound (no batch job in this PR) |
| ENTRY vs SUPERIOR | ENTRY 2/day on-demand; SUPERIOR 10/day (commercial on-demand Gastón) |

## Relevant files

| File | Action |
|------|--------|
| `domain/on_demand_entitlements.py` | New helper |
| `domain/services/messaging_service.py` | Wire entitlements |
| `docs/specs/on-demand-entitlements-sdd.md` | Lite spec |
| `tests/unit/domain/test_on_demand_entitlements.py` | New |
| `tests/unit/domain/test_messaging_service.py` | Tier + reset cases |

## Git policy (fixed)

Branch: `feat/tier-on-demand-entitlements` from `origin/main`. See [`docs/GIT_WORKFLOW.md`](docs/GIT_WORKFLOW.md#branch-names-preferred).

## Next after T024

**T030** `/workers/send-campaign` or **T012** completion / **T032** async webhook (per roadmap priority).

## Agent handoff

On-call: [`.cursor/agents/on-call.md`](.cursor/agents/on-call.md).
