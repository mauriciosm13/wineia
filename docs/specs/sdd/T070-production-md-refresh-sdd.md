# SDD — Refresh PRODUCTION.md after route changes (T070)

**Status:** implemented  
**Task:** [T070](../../ROADMAP-TASKS.md)  
**Comparison contract:** this Expected work list is what the reviewer checks against [T070-builder-report.md](./T070-builder-report.md).

## Problem

`docs/operations/PRODUCTION.md` drifts from the live HTTP surface, Datastore kinds, jobs/workers, and env knobs. Authors also lack a hard PR-time reminder beyond a GIT_WORKFLOW bullet (added in T071).

## Goals

- Audit PRODUCTION.md against current `main` (`api/routes.py`, customer/pre-sale paths, jobs/workers, Scheduler, queues, Datastore kinds, documented env).
- Fix any drift found; document the audit even when mostly in sync.
- Enforce process: GitHub PR template checkbox for PRODUCTION.md updates, plus DoD skill / ENGINEERING_MANUAL note. Extend GIT_WORKFLOW only if a light cross-link helps — do not duplicate T071 noisily.
- Mark T070 done when audit + process enforcement are in place.

## Non-goals

- Implementing T051 export/delete APIs or inventing those routes in PRODUCTION.md (note “pending T051 PR” if absent).
- T040–T043 payments; T004 GitHub admin.
- Product/runtime code under `api/`, `domain/`, `infrastructure/`, `tests/`.
- Flipping T050 / T071 / payments checkboxes.
- Rewriting PRODUCTION.md from scratch when a surgical sync suffices.

## Behavior

### Audit baseline (current `main`)

| Area | Source of truth |
|------|-----------------|
| HTTP paths | `api/routes.py` ROUTES + `api/handlers/customer_handler.py` (`/customers`, `/customers/{phone}`, `/customers/pre-sale`, `/customers/pre-sale/activate`) |
| Jobs / workers | `/jobs/send-recommendations`, `/jobs/send-weekly-education`, `/workers/send-message`, `/workers/send-campaign` — all require `X-Job-Internal-Secret` |
| Scheduler | `wine-send-recommendations`, `wine-send-weekly-education` (CD) |
| Queues | `core/queues.py`: `wine-messages` → send-message; `wine-campaigns` → send-campaign |
| Datastore kinds | `Customer`, `PreSaleCustomer`, `RecommendationContent`, `RecommendationHistory`, `ClaudeDailyBudget` |
| Env already documented | Job secret, webhook rate limits, `ON_DEMAND_DAILY_LIMIT_*`, `CLAUDE_DAILY_CALL_BUDGET`, `PRIVACY_POLICY_URL` / `TERMS_OF_SERVICE_URL` |
| T051 | No export/delete routes on `main` — note pending; do not invent paths |

### Process enforcement

1. `.github/PULL_REQUEST_TEMPLATE.md` includes a checkbox requiring `operations/PRODUCTION.md` updates when routes or production behavior change.
2. `.cursor/skills/definition-of-done/SKILL.md` states reviewers must confirm PRODUCTION.md sync when routes/behavior changed.
3. `docs/ENGINEERING_MANUAL.md` has a short note (ops or process) that PRODUCTION.md must stay in sync with routes/behavior.
4. `docs/GIT_WORKFLOW.md` already has the PRODUCTION checklist bullet from T071 — leave it; optional one-line pointer to the PR template only.

## Expected work

The builder implements only these items. The reviewer marks each **match**, **gap**, or **extra**.

| ID | Must be true when the work is done | Where |
|----|-------------------------------------|--------|
| EW-01 | PRODUCTION.md HTTP route table matches `api/routes.py` plus customer/pre-sale paths from the customer handler. Include an explicit row (or clear note) for `POST /customers/pre-sale/activate`. Paths present on `main`: `/health`, `/customers`, `/customers/{phone}`, `/customers/pre-sale`, `/customers/pre-sale/activate`, `/webhook/whatsapp`, `/jobs/send-recommendations`, `/jobs/send-weekly-education`, `/workers/send-message`, `/workers/send-campaign`, `/ia/suggestions`, `/recommendation-contents`. | `docs/operations/PRODUCTION.md` |
| EW-02 | Datastore kinds list includes exact kinds `Customer`, `PreSaleCustomer`, `RecommendationContent`, `RecommendationHistory`, and `ClaudeDailyBudget` (T061). | same |
| EW-03 | Jobs/workers/Scheduler sections remain accurate for the two CD Scheduler jobs and the four `/jobs/*` + `/workers/*` paths (secret header). Cloud Tasks queue names `wine-messages` and `wine-campaigns` are named in Integrations (or Async). | same |
| EW-04 | Config/env section still documents job secret, webhook rate limits, on-demand tier caps, `CLAUDE_DAILY_CALL_BUDGET`, and privacy/terms URLs (no regression). | same |
| EW-05 | PRODUCTION.md does **not** invent T051 export/delete routes. If those paths are absent on `main`, include an explicit short note that LGPD export/delete routes are pending the T051 PR. | same |
| EW-06 | `.github/PULL_REQUEST_TEMPLATE.md` exists with a checkbox that `operations/PRODUCTION.md` must be updated in the same PR when routes or production behavior change. | `.github/PULL_REQUEST_TEMPLATE.md` |
| EW-07 | `.cursor/skills/definition-of-done/SKILL.md` requires confirming PRODUCTION.md sync when routes or production behavior changed. `docs/ENGINEERING_MANUAL.md` has a short note to the same effect (ops or process section). Do not remove or rewrite the existing GIT_WORKFLOW PRODUCTION checkbox; optional one-line cross-link to the PR template only. | those files |
| EW-08 | Builder report documents the audit: what matched, what drifted, and that T051 routes were not invented. | `docs/specs/sdd/T070-builder-report.md` |
| EW-09 | Only after EW-01–EW-08 and EW-10 hold: `ROADMAP-TASKS.md` checks **only** T070; this SDD status is `implemented`; `INDEX.md` T070 row is `implemented`. Do not flip T050, T071, T051, or T040–T043. CL #64 may stay checked (already as-is); do not uncheck other CL items. | those files |
| EW-10 | Diff is docs/process only: no product code under `api/`, `domain/`, `infrastructure/`, or `tests/`. No payments implementation. No T051 APIs. | whole diff |

## Builder report

After implementation, write `docs/specs/sdd/T070-builder-report.md`:

| ID | Result (`done` or `skipped`) | Files | What changed |
|----|-------------------------------|-------|----------------|

Add a **Files touched** list of every path in the diff and verification notes. The reviewer treats any path not justified by an ID as **extra**. Include an **Audit findings** subsection.

## Reviewer comparison

Read this file, the builder report, and the diff. Return only:

- One line per ID: `EW-xx match|gap — evidence`
- Extras: paths or behavior not in the table
- Bugs that break an ID
- Verdict: accept or reject

Do not implement.

## Related

- [CONTEXT.md](../../../CONTEXT.md)
- [operations/PRODUCTION.md](../../operations/PRODUCTION.md)
- [GIT_WORKFLOW.md](../../GIT_WORKFLOW.md)
- [ENGINEERING_MANUAL.md](../../ENGINEERING_MANUAL.md)
- [T071-launch-checklist-doc-sdd.md](./T071-launch-checklist-doc-sdd.md) (prior PRODUCTION checklist bullet)
- [T051-export-delete-tooling-sdd.md](./T051-export-delete-tooling-sdd.md) (pending — do not invent routes)

## Revision history

| Date | Change |
|------|--------|
| 2026-11-10 | Initial SDD |
| 2026-11-18 | Orchestrator expands to T031-style Expected work EW-01–EW-10 (audit + PR template/DoD) |
| 2026-11-18 | Status → implemented after audit + process enforcement |
