# CONTEXT — WineAI (wineia)

> Read first. Product milestones: [`docs/ROADMAP.md`](docs/ROADMAP.md). Commercial launch checklist: [`docs/COMMERCIAL-LAUNCH.md`](docs/COMMERCIAL-LAUNCH.md). Micro-tasks: [`docs/ROADMAP-TASKS.md`](docs/ROADMAP-TASKS.md).

## Primary objective (current)

**T024** — Land tier-based **on-demand** entitlements for webhook IA (`messaging_service`). Done on branch `cursor/t024-on-demand-entitlements-afd2` (cherry-pick from `feat/tier-on-demand-entitlements`).

## Acceptance criteria (T024)

- [x] Replace hardcoded `DAILY_LIMIT` with `plan_tier` limits (ENTRY 2, SUPERIOR 10 — MVP defaults).
- [x] `messages_sent_today` + `daily_reset` UTC read-path reset.
- [x] Recommendation / education jobs unchanged.
- [x] Lite SDD `docs/specs/sdd/T024-on-demand-entitlements-sdd.md`; canonical detail `docs/specs/on-demand-entitlements-sdd.md`; PRODUCTION updated; T024 + CL #18a.
- [x] Unit tests: `on_demand_entitlements` + `messaging_service` tier/reset paths.
- [x] pytest, ruff, import style; domain/core coverage ≥ 95%.

## Decisions (T024)

| Topic | Decision |
|-------|----------|
| Limits | `domain/on_demand_entitlements.py` constants; **T060** may add config/ops tuning |
| Reset | Compare `daily_reset` to UTC calendar day on inbound (no batch job in this PR) |
| ENTRY vs SUPERIOR | ENTRY 2/day on-demand; SUPERIOR 10/day (commercial on-demand Gastón) |
| T012 | Webhook IP/phone limits remain infrastructure abuse layer — not product caps |

## Relevant files

| File | Role |
|------|------|
| `domain/on_demand_entitlements.py` | Tier caps, reset, `can_send_on_demand` |
| `domain/services/messaging_service.py` | Webhook path wiring |
| `docs/specs/on-demand-entitlements-sdd.md` | Normative behavior spec |
| `tests/unit/domain/test_on_demand_entitlements.py` | Entitlements unit tests |
| `tests/unit/domain/test_messaging_service.py` | Tier + reset integration in service |

## Git policy (fixed)

Branch: `cursor/t024-on-demand-entitlements-afd2` from `main`. See [`docs/GIT_WORKFLOW.md`](docs/GIT_WORKFLOW.md). **Never push to `main`.**

## Next after T024

**T030** `/workers/send-campaign`, or **T060** (externalize caps / ops tuning on top of T024 defaults).

## Agent handoff

On-call: [`.cursor/agents/on-call.md`](.cursor/agents/on-call.md).
