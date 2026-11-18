# Builder report — T071 Launch checklist document

**SDD:** [T071-launch-checklist-doc-sdd.md](./T071-launch-checklist-doc-sdd.md)  
**Branch:** `feat/t071-launch-checklist`  
**Date:** 2026-11-18

## Expected work

| ID | Result | Files | What changed |
|----|--------|-------|--------------|
| EW-01 | done | `docs/LAUNCH-CHECKLIST.md` | New operator go-live checklist with checkbox sections: tag/`workflow_dispatch` deploy; Secret Manager/env including `JOB_INTERNAL_SECRET`, `ON_DEMAND_DAILY_LIMIT_*`, `CLAUDE_DAILY_CALL_BUDGET` (`0`/unset = unlimited); Scheduler smoke for both CD jobs; Twilio webhook signature; Cloud Tasks workers (`send-message` / `send-campaign`); `GET /health`; entitlements/budget notes (T060/T061); `/ia/suggestions` must not be public; links to PRODUCTION, DEPLOYMENT, threat-model, SDD INDEX, COMMERCIAL-LAUNCH, INCIDENT-RESPONSE. |
| EW-02 | done | same | Section **9. Payments (deferred)**: T040–T043 parked; manual provisioning until payments land; no provider claimed as decided; CL #55 / payments-evaluation pointers only. |
| EW-03 | done | `docs/COMMERCIAL-LAUNCH.md` | Item 68 checked and linked to `./LAUNCH-CHECKLIST.md`. |
| EW-04 | done | `docs/ENGINEERING_MANUAL.md` | Product and planning table row for `LAUNCH-CHECKLIST.md` (CL #68). |
| EW-05 | done | `docs/GIT_WORKFLOW.md` | PR checklist bullet: update `operations/PRODUCTION.md` in the same PR when routes or production behavior change. T070 left unchecked. |
| EW-06 | done | `docs/ROADMAP-TASKS.md`, `docs/COMMERCIAL-LAUNCH.md`, `docs/specs/sdd/T071-launch-checklist-doc-sdd.md`, `docs/specs/sdd/INDEX.md` | Flipped only after EW-01–EW-05 and EW-07 gate: T071 checked (+ link); CL #68 checked; SDD status `implemented`; INDEX T071 `implemented`. T050/T070/T040–T043 untouched. Summary count 10→11. |
| EW-07 | done | whole diff | Docs/handoff only. No `api/`, `domain/`, `infrastructure/`, or `tests/` product code in the staged T071 commit. No payments implementation. No T050 status or LGPD code. |

## Deviations from the SDD / SPEC

1. Handoff files `CONTEXT.md`, `PLAN.md`, `SPEC.md` are included for orchestrator continuity (same pattern as prior T0xx runs). They are not Expected work products.
2. `ROADMAP-TASKS.md` summary line updated to “11 done” alongside the T071 checkbox (justified by EW-06).

## Files touched

| Path | EW |
|------|----|
| `docs/LAUNCH-CHECKLIST.md` (new) | EW-01, EW-02 |
| `docs/COMMERCIAL-LAUNCH.md` | EW-03, EW-06 |
| `docs/ENGINEERING_MANUAL.md` | EW-04 |
| `docs/GIT_WORKFLOW.md` | EW-05 |
| `docs/ROADMAP-TASKS.md` | EW-06 |
| `docs/specs/sdd/T071-launch-checklist-doc-sdd.md` | EW-01–EW-07 contract; EW-06 status |
| `docs/specs/sdd/INDEX.md` | EW-06 |
| `docs/specs/sdd/T071-builder-report.md` (new) | this report |
| `CONTEXT.md` | handoff (not an EW product) |
| `PLAN.md` | handoff |
| `SPEC.md` | handoff |

## Verification commands and results

Docs-only change; no runtime tests required by EW-07.

| Command | Result |
|---------|--------|
| `git diff --name-only` (staged T071 set) | Only docs + CONTEXT/PLAN/SPEC + builder report; no runtime product paths |
| Confirm T050/T070/T040–T043 checkboxes unchanged in ROADMAP-TASKS / INDEX | Pass — only T071 flipped |
| Confirm `docs/LAUNCH-CHECKLIST.md` contains required env names and deferred payments section | Pass |
