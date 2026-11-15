# CONTEXT — WineAI (wineia)

> Read first. Product milestones: [`docs/ROADMAP.md`](docs/ROADMAP.md). Commercial launch checklist: [`docs/COMMERCIAL-LAUNCH.md`](docs/COMMERCIAL-LAUNCH.md). Micro-tasks: [`docs/ROADMAP-TASKS.md`](docs/ROADMAP-TASKS.md).

## Primary objective (current)

**T060** — Per-user daily IA turn limit by plan tier, with **ops-tunable caps** via env on top of T024 entitlements. ENTRY and SUPERIOR daily on-demand limits stay at code defaults **2 / 10** when env is unset; when set, `core/config.py` supplies overrides consumed by `domain/on_demand_entitlements.py`.

The comparison contract is [`docs/specs/sdd/T060-per-tier-ia-caps-sdd.md`](docs/specs/sdd/T060-per-tier-ia-caps-sdd.md). Its **Expected work** list (EW-01…) is what the reviewer checks against the builder report. Do not add behavior that list does not name. On conflict, the SDD Expected work table wins over PLAN.md / SPEC.md.

## Priority / skip (parent, 2026-11-15)

| Item | Action |
|------|--------|
| **T040–T043** (payments) | **Parked.** Do not work. Leave ROADMAP unchecked. Do not reopen closed PR #36. Do not mark Asaas as decided on `main`. |
| **T004** | Skip (GitHub admin). |
| **T050 / T051** | Skip this run (LGPD waits; product-side first). |
| **This run** | **T060** only. |

## Decisions already made (parent defaults, 2026-11-15)

| Topic | Decision |
|-------|----------|
| T024 defaults | ENTRY=2 / SUPERIOR=10 remain **code defaults** when env unset. |
| Configurability | Caps configurable via env (e.g. `ON_DEMAND_DAILY_LIMIT_ENTRY`, `ON_DEMAND_DAILY_LIMIT_SUPERIOR`) read through `core/config.py`, consumed by `on_demand_entitlements`. No hardcode-only map left as the sole source when env is set; document defaults when unset. |
| Out of scope siblings | No change to T012 webhook abuse limits, T021 cadence, or T061 (global budget). |
| Clean Architecture | Domain must not import infrastructure; config via `core` is OK (existing pattern). |
| Tests | Unit tests for default + env override; coverage ≥95% domain/core; ruff + import style. |
| Docs / status | Update PRODUCTION / DEPLOYMENT / COMMERCIAL-LAUNCH #28 as needed; check T060 + SDD/INDEX implemented when EW hold. |
| Git | English Conventional Commits; never `main`. Branch: `feat/t060-per-tier-ia-caps` (**no** `cursor/` prefix). Parent opens PR. |

## Decisions made by the orchestrator

| Topic | Decision |
|-------|----------|
| Env var names | `ON_DEMAND_DAILY_LIMIT_ENTRY` and `ON_DEMAND_DAILY_LIMIT_SUPERIOR` (integers ≥ 0). Invalid/empty → fall back to defaults 2 / 10. |
| Config API | `core/config.py` exposes getters (or settings fields) for both limits; `on_demand_entitlements` reads those instead of a private hardcode-only dict as sole source. |
| Legacy | Root `config.py` `ESSENTIAL_DAILY_LIMIT` is unused; leave alone — do not invent a second limit system. |
| Messaging | `messaging_service` keeps using `can_send_message` / entitlement helpers; no change to T012, cadence, or enqueue paths beyond reading new caps. |
| Scope discipline | Do not touch payments, LGPD, T061 global budget, or webhook rate-limit algorithms. |
| CL #28 | Update wording: per-user ops-tunable caps delivered (T060); leave unchecked pending T061 global budget. |

## Out of scope

- T040–T043 payments / provider choice / Asaas.
- T004 GitHub admin.
- T050 / T051 LGPD.
- T061 global Claude/Twilio budget.
- T012 webhook IP/phone abuse limits.
- T021 entry cadence.
- New pip dependencies; changing plan-tier field shapes beyond reading limits.
- Making caps per-customer overrides in Datastore (env/ops only this run).

## Relevant files

| File | Role |
|------|------|
| `docs/specs/sdd/T060-per-tier-ia-caps-sdd.md` | Stub → expand to T031-style with Expected work EW-xx |
| `docs/specs/sdd/T031-scheduler-deploy-cd-sdd.md` | Template for SDD + EW style |
| `docs/specs/sdd/T031-builder-report.md` | Template for builder report |
| `domain/on_demand_entitlements.py` | T024 entitlement logic; consume config caps |
| `docs/specs/on-demand-entitlements-sdd.md` | T024 SDD / contract |
| `core/config.py` | Env → typed config; add ON_DEMAND_DAILY_LIMIT_* |
| `domain/services/messaging_service.py` | Uses entitlements for daily IA gate |
| `docs/COMMERCIAL-LAUNCH.md` | Item #28 |
| `docs/decision.md` | Architecture / product decisions |
| `docs/operations/PRODUCTION.md`, `docs/DEPLOYMENT.md` | Ops env documentation |
| `docs/ROADMAP.md`, `docs/ROADMAP-TASKS.md`, `docs/specs/sdd/INDEX.md` | Status flips after EW hold |
| `PLAN.md`, `SPEC.md` | Plan/spec updates for T060 |
| `tests/unit/domain/` (entitlements / messaging) | Default + env override tests |
| `docs/specs/sdd/T060-builder-report.md` | Builder report for reviewer judge |

## Acceptance criteria

See EW-01… in the SDD. In short:

- [ ] ENTRY/SUPERIOR daily IA caps default to 2/10; env overrides via `core/config` → `on_demand_entitlements`.
- [ ] Unit tests cover defaults and env overrides; domain/core coverage ≥ 95%; ruff + import style pass.
- [ ] No change to T012 / T021 / T061 / payments / LGPD.
- [ ] PRODUCTION / DEPLOYMENT / COMMERCIAL-LAUNCH #28 / ROADMAP / INDEX updated when EW hold.
- [ ] Builder report + reviewer judge accept (each EW vs change list AND diff → match|gap|extra).

## Git policy (fixed)

Branch: `feat/t060-per-tier-ia-caps` from `origin/main` (no `cursor/` prefix — see [`docs/GIT_WORKFLOW.md`](docs/GIT_WORKFLOW.md)). **Never push to `main`.** Conventional Commits, English, lowercase subject. Parent creates the GitHub PR; leave PR URL unset if ManagePullRequest is parent-owned. Commit bodies wrap at 72 characters (commitlint `body-max-line-length` is 100).

## Agent handoff

On-call: [`.cursor/agents/on-call.md`](.cursor/agents/on-call.md).

Builder report path: `docs/specs/sdd/T060-builder-report.md` (one row per Expected work ID, files, done or skipped, plus Files touched). The reviewer reads that file, the SDD, and the diff, and is the judge. The reviewer does not edit any file.
