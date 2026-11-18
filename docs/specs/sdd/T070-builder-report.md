# Builder report — T070 Refresh PRODUCTION.md after route changes

**SDD:** [T070-production-md-refresh-sdd.md](./T070-production-md-refresh-sdd.md)  
**Branch:** `feat/t070-production-md-refresh`  
**Date:** 2026-11-18

## Audit findings

Compared `docs/operations/PRODUCTION.md` on `main` to `api/routes.py`,
`api/handlers/customer_handler.py`, `infrastructure/repositories/*` KIND
constants, `core/queues.py`, Scheduler docs, and config/env notes.

| Area | Result |
|------|--------|
| ROUTES table paths (`/health`, jobs, workers, webhook, ia, recommendation-contents) | Already present and accurate |
| `/customers`, `/customers/{phone}`, `/customers/pre-sale` | Present; methods clarified |
| `/customers/pre-sale/activate` | **Drift** — handler path existed; missing as its own route row → added |
| Jobs/workers secret header | Accurate; weekly-education job row now also states secret requirement |
| Scheduler (two CD jobs) | Already accurate — unchanged |
| Datastore kinds | **Drift** — prose omitted `ClaudeDailyBudget` and used informal names → exact kinds listed |
| Cloud Tasks queue names | **Drift** — pointed at `core/queues.py` only → named `wine-messages` / `wine-campaigns` |
| Env (job secret, rate limits, on-demand caps, Claude budget, privacy URLs) | Already accurate — no regression |
| T051 export/delete routes | Absent on `main` — **not invented**; pending-T051 note added |
| Process: PR template | Missing → added |
| Process: DoD / ENGINEERING_MANUAL | Weak/absent PRODUCTION sync → strengthened |
| Process: GIT_WORKFLOW | Already had PRODUCTION checkbox (T071) — one-line PR template cross-link only |

## Expected work

| ID | Result | Files | What changed |
|----|--------|-------|--------------|
| EW-01 | done | `docs/operations/PRODUCTION.md` | Route table header notes customer handler; added `/customers/pre-sale/activate` row; clarified customer/pre-sale methods; `/ia/suggestions` marked operator/internal. All `main` paths covered. |
| EW-02 | done | same | Integrations DB line lists `Customer`, `PreSaleCustomer`, `RecommendationContent`, `RecommendationHistory`, `ClaudeDailyBudget`. |
| EW-03 | done | same | Scheduler table unchanged (still accurate). Jobs/workers still document secret; weekly-education row now says requires `X-Job-Internal-Secret`. Async line names `wine-messages` and `wine-campaigns` with worker paths. |
| EW-04 | done | same | Config section unchanged for job secret, webhook rate limits, `CLAUDE_DAILY_CALL_BUDGET`, privacy/terms URLs; on-demand caps remain in webhook route notes. |
| EW-05 | done | same | Explicit note: LGPD export/delete routes pending T051 PR; no invented paths. |
| EW-06 | done | `.github/PULL_REQUEST_TEMPLATE.md` | New template with PRODUCTION.md checkbox (plus semantic/commitlint/CI/docs items). |
| EW-07 | done | `.cursor/skills/definition-of-done/SKILL.md`, `docs/ENGINEERING_MANUAL.md`, `docs/GIT_WORKFLOW.md` | DoD requires PRODUCTION sync; ENGINEERING_MANUAL ops note + links; GIT_WORKFLOW keeps existing checkbox and adds one-line PR template pointer. |
| EW-08 | done | `docs/specs/sdd/T070-builder-report.md` | This report: audit table + EW rows + files touched. |
| EW-09 | done | `docs/ROADMAP-TASKS.md`, `docs/specs/sdd/T070-production-md-refresh-sdd.md`, `docs/specs/sdd/INDEX.md` | Flipped only after EW-01–EW-08 and EW-10 gate: T070 checked; summary 11→12; SDD status `implemented`; INDEX T070 `implemented`. T050/T071/T051/T040–T043 untouched. CL #64 left checked. |
| EW-10 | done | whole diff | Docs/process/handoff only. No `api/`, `domain/`, `infrastructure/`, or `tests/` product code. No payments. No T051 APIs. |

## Deviations from the SDD / SPEC

1. Handoff files `CONTEXT.md`, `PLAN.md`, `SPEC.md` are included for orchestrator continuity (same pattern as prior T0xx runs). They are not Expected work products.
2. `/ia/suggestions` note “must not be public” is operational guidance already used in T071 launch checklist; not a new route.

## Files touched

| Path | EW |
|------|----|
| `docs/operations/PRODUCTION.md` | EW-01–EW-05 |
| `.github/PULL_REQUEST_TEMPLATE.md` (new) | EW-06 |
| `.cursor/skills/definition-of-done/SKILL.md` | EW-07 |
| `docs/ENGINEERING_MANUAL.md` | EW-07 |
| `docs/GIT_WORKFLOW.md` | EW-07 |
| `docs/ROADMAP-TASKS.md` | EW-09 |
| `docs/specs/sdd/T070-production-md-refresh-sdd.md` | EW-01–EW-10 contract; EW-09 status |
| `docs/specs/sdd/INDEX.md` | EW-09 |
| `docs/specs/sdd/T070-builder-report.md` (new) | EW-08 |
| `CONTEXT.md` | handoff (not an EW product) |
| `PLAN.md` | handoff |
| `SPEC.md` | handoff |

## Verification commands and results

Docs/process only; no runtime tests required by EW-10.

| Command | Result |
|---------|--------|
| Diff vs `api/routes.py` + customer handler paths | All listed paths present in PRODUCTION; activate + T051 note present |
| Confirm KIND list matches repository KIND constants | Pass — five kinds named |
| Confirm queue names match `core/queues.py` | Pass — `wine-messages`, `wine-campaigns` |
| Confirm T050/T071/T051/T040–T043 checkboxes unchanged | Pass — only T070 flipped |
| Confirm no `api/` `domain/` `infrastructure/` `tests/` in T070 change set | Pass (handoff + docs/process only) |
