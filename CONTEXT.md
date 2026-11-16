# CONTEXT — WineAI (wineia)

> Read first. Product milestones: [`docs/ROADMAP.md`](docs/ROADMAP.md). Commercial launch checklist: [`docs/COMMERCIAL-LAUNCH.md`](docs/COMMERCIAL-LAUNCH.md). Micro-tasks: [`docs/ROADMAP-TASKS.md`](docs/ROADMAP-TASKS.md).

## Primary objective (current)

**T061** — Global Claude budget stop (remaining half of COMMERCIAL-LAUNCH #28). Cap total Claude API **call count** per **UTC calendar day** via env; fail closed before new generation when over budget. Ops map calls→USD offline.

The comparison contract is [`docs/specs/sdd/T061-global-claude-budget-stop-sdd.md`](docs/specs/sdd/T061-global-claude-budget-stop-sdd.md). Its **Expected work** list (EW-01…) is what the reviewer checks against the builder report. Do not add behavior that list does not name. On conflict, the SDD Expected work table wins over PLAN.md / SPEC.md.

## Priority / skip (parent, 2026-11-16)

| Item | Action |
|------|--------|
| **T040–T043** (payments) | **Parked.** Do not work. Leave ROADMAP unchecked. Do not reopen closed PR #36. Do not mark Asaas as decided on `main`. |
| **T004** | Skip (GitHub admin). |
| **T050 / T051** | Skip this run (LGPD waits; product-side first). |
| **This run** | **T061** only. |

## Decisions already made (parent defaults, 2026-11-16)

| Topic | Decision |
|-------|----------|
| Budget unit | Claude API **call count** per **UTC calendar day** (not USD). |
| Env | `CLAUDE_DAILY_CALL_BUDGET` via `core/config.py` (integer). **`0` or unset = unlimited** (local/dev safe). When `> 0`, enforce fail-closed before any new generation. Invalid/empty/negative → treat as `0` (unlimited). |
| Persistence | Datastore entity (day key + count) behind a **domain-facing port/interface**; infrastructure implements it. Domain/IA path must not import the Datastore **client** directly. |
| Enforcement | Single choke point used by all Claude generations (`IAService` methods / shared helper wrapping `ClaudeClient.generate`) so webhook, recommendation, education, and `/ia/suggestions` respect the budget. |
| Over budget | Do **not** call Claude. Raise a clear domain error (`ClaudeBudgetExceededError`) or skip path. Jobs (`send_recommendations`, `send_weekly_education`) **log skip reason** and do not fan-out IA text. Webhook/messaging: short Portuguese “service temporarily unavailable” message without burning Claude; do not increment `messages_sent_today`. |
| Increment | Increment counter only after a **successful** Claude response (accept small race overshoot across instances). Failed/empty generation that raises before success does not increment. |
| Alerting | Out of scope: PagerDuty / alerting webhooks. Ops watch logs + Anthropic billing. |
| Keep both | T012 webhook rate limits and T060 per-user caps stay; do not rewrite them. |
| Out of scope | Monthly budget; payments T040–T043; LGPD T050/T051; T004; new pip deps. |
| Status | Mark T061 + CL #28 **complete** when EW hold (T060 already delivered per-user caps). Update INDEX/SDD/PRODUCTION/DEPLOYMENT/threat-model/decision as needed. |
| Git | English Conventional Commits; never `main`. Branch: `feat/t061-global-claude-budget` (**no** `cursor/` prefix, no `-afd2`). Parent opens PR. |

## Decisions made by the orchestrator

| Topic | Decision |
|-------|----------|
| Config default | `CLAUDE_DAILY_CALL_BUDGET = 0` when unset/empty/invalid/negative (unlimited). |
| Day key | UTC `YYYY-MM-DD` string as Datastore entity key name; kind `ClaudeDailyBudget`; property `call_count` (int). |
| Domain port | `domain/repositories/claude_budget_repository.py` ABC with `get_call_count(day_key)` and `increment_call_count(day_key)`. Helpers + `ClaudeBudgetExceededError` in `domain/claude_budget.py`. |
| Choke point | Private helper on `IAService` (or module helper) that: if budget `> 0`, check count ≥ budget → raise; else call `ClaudeClient.generate`; on success increment. All three `generate_*` methods use it. |
| Job logging | `core.logging.log_info` with explicit skip reason string containing `claude daily call budget exceeded`. |
| Unavailable copy | Portuguese: `Desculpe, o serviço está temporariamente indisponível. Tente novamente em breve.` |
| Wiring | `IAService` accepts optional `budget_repository`; when budget `> 0` and repo is None, lazy-default to `DatastoreClaudeBudgetRepository` (same infra-from-service pattern as recommendation/education). When budget is `0`, never touch the repo. |
| CL #28 | Check complete: T060 per-user caps + T061 global call budget both done. |

## Out of scope

- T040–T043 payments / provider choice / Asaas.
- T004 GitHub admin.
- T050 / T051 LGPD.
- T012 webhook IP/phone abuse limit algorithms.
- T060 per-tier cap rewrite (keep as-is).
- Monthly Claude budget; USD spend tracking; PagerDuty/alerting webhooks.
- New pip dependencies; `docs/MVP_SCOPE.md`.

## Relevant files

| File | Role |
|------|------|
| `docs/specs/sdd/T061-global-claude-budget-stop-sdd.md` | Stub → expand to T031-style with Expected work EW-xx |
| `docs/specs/sdd/T031-scheduler-deploy-cd-sdd.md` | Template for SDD + EW style |
| `docs/specs/sdd/T031-builder-report.md` | Template for builder report |
| `docs/specs/sdd/T060-per-tier-ia-caps-sdd.md` | Env pattern reference |
| `domain/services/ia_service.py` | Choke point for all Claude generations |
| `infrastructure/external/claude_client.py` | Claude API client (wrapped, not rewritten) |
| `domain/services/messaging_service.py` | Webhook path: unavailable message on budget exceed |
| `domain/services/recommendation_service.py` | Job: skip + log, no fan-out |
| `domain/services/education_service.py` | Job: skip + log, no fan-out |
| `core/config.py` | Add `CLAUDE_DAILY_CALL_BUDGET` |
| `core/logging.py` | Job skip logging |
| `docs/COMMERCIAL-LAUNCH.md` | Item #28 |
| `docs/threat-model.md` | §4.3 product rate limits |
| `docs/decision.md` | Product / IA cost |
| `docs/operations/PRODUCTION.md`, `docs/DEPLOYMENT.md` | Ops env documentation |
| `docs/ROADMAP-TASKS.md`, `docs/specs/sdd/INDEX.md` | Status flips after EW hold |
| `PLAN.md`, `SPEC.md` | Plan/spec updates for T061 |
| `docs/specs/sdd/T061-builder-report.md` | Builder report for reviewer judge |

## Acceptance criteria

See EW-01… in the SDD. In short:

- [ ] `CLAUDE_DAILY_CALL_BUDGET` via `core/config`; 0/unset = unlimited; `> 0` fail-closed before Claude.
- [ ] Domain port + Datastore implementation; UTC day counter; increment after successful generate.
- [ ] Single choke point in `IAService`; jobs log skip / no fan-out; messaging PT unavailable without burning Claude.
- [ ] Unit tests; domain/core coverage ≥ 95%; ruff + import style pass.
- [ ] No change to payments / LGPD / T012 algorithms / T060 rewrite.
- [ ] PRODUCTION / DEPLOYMENT / threat-model / decision / COMMERCIAL-LAUNCH #28 / ROADMAP-TASKS / INDEX updated when EW hold.
- [ ] Builder report + reviewer judge accept (each EW vs change list AND diff → match|gap|extra).

## Git policy (fixed)

Branch: `feat/t061-global-claude-budget` from `origin/main` (no `cursor/` prefix — see [`docs/GIT_WORKFLOW.md`](docs/GIT_WORKFLOW.md)). **Never push to `main`.** Conventional Commits, English, lowercase subject. Parent creates the GitHub PR; leave PR URL unset if ManagePullRequest is parent-owned. Commit bodies wrap at 72 characters (commitlint `body-max-line-length` is 100).

## Agent handoff

On-call: [`.cursor/agents/on-call.md`](.cursor/agents/on-call.md).

Builder report path: `docs/specs/sdd/T061-builder-report.md` (one row per Expected work ID, files, done or skipped, plus Files touched). The reviewer reads that file, the SDD, and the diff, and is the judge. The reviewer does not edit any file.
