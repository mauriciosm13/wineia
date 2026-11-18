# SDD — Launch checklist document (T071)

**Status:** implemented  
**Task:** [T071](../../ROADMAP-TASKS.md)  
**Comparison contract:** this Expected work list is what the reviewer checks against [T071-builder-report.md](./T071-builder-report.md).

## Problem

Commercial launch needs a single operator go-live checklist (CL #68). `COMMERCIAL-LAUNCH.md` tracks phased product gates; it does not give operators a signed verification path after a production tag or `workflow_dispatch` deploy.

## Goals

- Add `docs/LAUNCH-CHECKLIST.md` as the operator go-live verification document.
- Cover deploy, secrets/env, Scheduler smoke, Twilio signature, Cloud Tasks workers, health, entitlements/budget, and deferred payments.
- Cross-link threat-model, key SDDs, DEPLOYMENT, and PRODUCTION.
- Link from COMMERCIAL-LAUNCH #68 and ENGINEERING_MANUAL.
- Mark T071 + CL #68 complete when Expected work holds.

## Non-goals

- T040–T043 payments implementation or provider choice.
- T004 GitHub admin.
- T050 / T051 LGPD code paths or status flips (parallel work may own T050).
- Full T070 PRODUCTION.md refresh ownership (optional one-line sync reminder only).
- Runtime API / domain / infrastructure code changes.
- Rewriting COMMERCIAL-LAUNCH phase lists into the new checklist.
- New pip dependencies; `docs/MVP_SCOPE.md`.

## Behavior

### Operator checklist document

`docs/LAUNCH-CHECKLIST.md` is the signed go-live path. It is complementary to [COMMERCIAL-LAUNCH.md](../../COMMERCIAL-LAUNCH.md): phases stay there; verification steps live here.

Required sections (checkbox style, English):

1. **Deploy** — confirm production release via tag `v*.*.*` or `workflow_dispatch`; Cloud Run revision healthy; not auto-deploy from `main`.
2. **Secrets / env** — Secret Manager / Cloud Run env present for Twilio, Anthropic/IA, GCP queue URL vars, and at least: `JOB_INTERNAL_SECRET`, `ON_DEMAND_DAILY_LIMIT_ENTRY`, `ON_DEMAND_DAILY_LIMIT_SUPERIOR`, `CLAUDE_DAILY_CALL_BUDGET` (document that `0`/unset = unlimited for the global budget).
3. **Scheduler smoke** — both CD jobs (`wine-send-recommendations`, `wine-send-weekly-education`) exist; headers include `X-Job-Internal-Secret`; optional dry/manual invoke notes point at DEPLOYMENT / PRODUCTION.
4. **Twilio webhook signature** — inbound `/webhook/whatsapp` rejects invalid signatures; Twilio console webhook URL points at live Cloud Run.
5. **Cloud Tasks workers** — queues `wine-messages` / `wine-campaigns` → `/workers/send-message` and `/workers/send-campaign`; worker routes require job secret.
6. **Health** — `GET /health` returns success on the live URL.
7. **Entitlements / budget notes** — per-tier on-demand caps (T060) and global Claude call budget (T061); ops watch logs / Anthropic billing.
8. **Security / exposure** — `/ia/suggestions` must not be public in production (network restriction or future auth); link [threat-model.md](../../threat-model.md).
9. **Payments (deferred)** — T040–T043 parked; launch uses **manual provisioning** until payments land; do not claim a provider is chosen.
10. **Doc links** — PRODUCTION, DEPLOYMENT, threat-model, SDD index (and/or key SDDs), COMMERCIAL-LAUNCH, INCIDENT-RESPONSE.

### Cross-links and status

- COMMERCIAL-LAUNCH item 68 links to `LAUNCH-CHECKLIST.md` and is checked when EW hold.
- ENGINEERING_MANUAL lists the launch checklist under product/planning or production/incidents.
- Optional: GIT_WORKFLOW PR checklist reminds authors to keep `operations/PRODUCTION.md` in sync when routes/behavior change (T070 spirit; does not flip T070).

## Expected work

The builder implements only these items. The reviewer marks each **match**, **gap**, or **extra**.

| ID | Must be true when the work is done | Where |
|----|-------------------------------------|--------|
| EW-01 | `docs/LAUNCH-CHECKLIST.md` exists as an operator go-live checklist with checkbox steps covering: tag/`workflow_dispatch` deploy verification; Secret Manager/env including `JOB_INTERNAL_SECRET`, `ON_DEMAND_DAILY_LIMIT_*`, `CLAUDE_DAILY_CALL_BUDGET`; Scheduler jobs smoke for both CD jobs; Twilio webhook signature; Cloud Tasks workers (`send-message` / `send-campaign`); `GET /health`; entitlements/budget notes (T060/T061); `/ia/suggestions` must not be public; links to PRODUCTION, DEPLOYMENT, threat-model, and SDD index or key SDDs. | `docs/LAUNCH-CHECKLIST.md` |
| EW-02 | Checklist has an explicit **Payments deferred** section: T040–T043 parked; commercial launch uses manual customer provisioning until payments work lands; no payment provider claimed as decided. | same |
| EW-03 | `docs/COMMERCIAL-LAUNCH.md` item 68 links to `LAUNCH-CHECKLIST.md` (path relative under `docs/`). | `docs/COMMERCIAL-LAUNCH.md` |
| EW-04 | `docs/ENGINEERING_MANUAL.md` links to `LAUNCH-CHECKLIST.md` in an appropriate table (product/planning or production/incidents). | `docs/ENGINEERING_MANUAL.md` |
| EW-05 | `docs/GIT_WORKFLOW.md` PR checklist (or equivalent short note) states that `operations/PRODUCTION.md` must stay in sync when routes or production behavior change. Do not create a PR template solely for this. Do not flip T070. | `docs/GIT_WORKFLOW.md` |
| EW-06 | Only after EW-01–EW-05 and EW-07 hold: `ROADMAP-TASKS.md` checks **only** T071; `COMMERCIAL-LAUNCH.md` checks item 68; this SDD status is `implemented`; `INDEX.md` T071 row is `implemented`. Do not flip T050, T070, or T040–T043. | those files |
| EW-07 | Diff is docs-only for T071 deliverables. No runtime `api/`, `domain/`, `infrastructure/`, or `tests/` product code. No payments implementation. No T050 status or LGPD code changes. | whole diff |

## Builder report

After implementation, write `docs/specs/sdd/T071-builder-report.md`:

| ID | Result (`done` or `skipped`) | Files | What changed |
|----|-------------------------------|-------|----------------|

Add a **Files touched** list of every path in the diff and the exact verification commands with results. The reviewer treats any path not justified by an ID as **extra**.

## Reviewer comparison

Read this file, the builder report, and the diff. Return only:

- One line per ID: `EW-xx match|gap — evidence`
- Extras: paths or behavior not in the table
- Bugs that break an ID or would mislead an operator at go-live
- Verdict: accept or reject

Do not implement.

## Related

- [CONTEXT.md](../../../CONTEXT.md)
- [COMMERCIAL-LAUNCH.md](../../COMMERCIAL-LAUNCH.md) — #68
- [ENGINEERING_MANUAL.md](../../ENGINEERING_MANUAL.md)
- [operations/PRODUCTION.md](../../operations/PRODUCTION.md)
- [DEPLOYMENT.md](../../DEPLOYMENT.md)
- [threat-model.md](../../threat-model.md)
- [INDEX.md](./INDEX.md)

## Revision history

| Date | Change |
|------|--------|
| 2026-11-10 | Initial SDD |
| 2026-11-18 | Expand to T031-style Expected work EW-01–EW-07 from parent T071 decisions |
| 2026-11-18 | Status `implemented` after EW-01–EW-07 hold |
