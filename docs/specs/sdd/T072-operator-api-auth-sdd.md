# SDD — Operator API authentication (T072)

**Status:** implemented  
**Task:** [T072](../../ROADMAP-TASKS.md)  
**Comparison contract:** this Expected work list is what the reviewer checks against [T072-builder-report.md](./T072-builder-report.md).

## Problem

Threat model and `decision.md` flag operator HTTP surfaces as a launch blocker: `/customers*`, `/ia/suggestions`, and `/recommendation-contents` have **no application auth**. Anyone who can reach the Cloud Run URL can read/alter customers, trigger Claude, and create catalog content. Jobs/workers already use `JOB_INTERNAL_SECRET` + `X-Job-Internal-Secret` (T010). Operator surfaces must reuse that same control and fail closed when the secret is unset.

## Goals

- Protect operator paths with the **same** `JOB_INTERNAL_SECRET` and header `X-Job-Internal-Secret`, reusing `api/internal_job_auth.py` (constant-time compare, 401 JSON, fail closed).
- Keep `/health` open; keep `/webhook/whatsapp` on Twilio signature (+ rate limits); keep `/jobs/*` and `/workers/*` gated as today.
- Update PRODUCTION, DEPLOYMENT, threat-model, decision.md, LAUNCH-CHECKLIST, LGPD runbook; register T072 in INDEX + ROADMAP-TASKS; mark CL #19 for authenticated operator API (tier via existing customer PATCH).
- Unit tests for the router auth matrix.

## Non-goals

- T040–T043 payments; T004; Dependabot; WhatsApp templates; retention-policy docs.
- A second secret, OIDC, IAP, or Cloud Run IAM changes in application code.
- New “add-on” product APIs.
- New pip dependencies.

## Behavior

### Path matrix

| Path | Auth |
|------|------|
| `/customers`, `/customers/*` (CRUD, pre-sale, export, erase) | Require `X-Job-Internal-Secret` matching `JOB_INTERNAL_SECRET` |
| `/ia/suggestions` | Same |
| `/recommendation-contents` | Same |
| `/jobs/*`, `/workers/*` | Same (already implemented; must keep working) |
| `/health` | No secret |
| `/webhook/whatsapp` | No secret; Twilio signature + rate limits unchanged |

### Failure modes

| Condition | Result |
|-----------|--------|
| Secret unset / empty | 401 for all gated paths (fail closed) |
| Header missing or wrong | 401 `{"error": "unauthorized"}` |
| Header matches | Handler runs as before |

### Implementation

Extend `path_requires_internal_job_auth(path)` in `api/internal_job_auth.py` so it returns True for operator surfaces in addition to `/jobs/*` and `/workers/*`. `api/routes.py` already calls that helper before dispatch — no second middleware. Reuse `internal_job_request_is_authorized` and `reject_unauthorized_internal_job`.

## Expected work

The builder implements only these items. The reviewer marks each **match**, **gap**, or **extra**.

| ID | Must be true when the work is done | Where |
|----|-------------------------------------|--------|
| EW-01 | `path_requires_internal_job_auth` returns True for `/customers`, any `/customers/...` path, `/ia/suggestions`, and `/recommendation-contents`, and still True for `/jobs/*` and `/workers/*`. Returns False for `/health` and `/webhook/whatsapp`. | `api/internal_job_auth.py` |
| EW-02 | Router rejects operator paths without a valid secret (missing header, wrong header, or unset `JOB_INTERNAL_SECRET`) with **401** before the handler runs. Valid secret reaches the handler. Jobs/workers behavior unchanged. `/health` and `/webhook/whatsapp` do not require the secret. | `api/routes.py`, `tests/unit/api/test_internal_job_auth.py` |
| EW-03 | Unit tests cover the auth matrix: at least one protected operator path each for customers / ia / recommendation-contents; open paths health + webhook; fail-closed when secret unset; accept with valid secret. | `tests/unit/api/test_internal_job_auth.py` |
| EW-04 | Docs: `PRODUCTION.md` states operator routes require `X-Job-Internal-Secret`; `DEPLOYMENT.md` documents that the same secret covers operator APIs (not only jobs/workers); `threat-model.md` updates entry-point table and §4.5; `decision.md` closes the unauthenticated-operator gap; `LAUNCH-CHECKLIST.md` checks operator API secret gating; `LGPD-EXPORT-DELETE.md` curl examples send the header. | those files |
| EW-05 | `ROADMAP-TASKS.md` adds and checks **T072**; `INDEX.md` T072 row `implemented`; this SDD status `implemented`; `COMMERCIAL-LAUNCH.md` item **19** checked with wording that operator API is authenticated (`JOB_INTERNAL_SECRET`); tier via existing customer PATCH; add-on N/A until product defines add-ons. `CONTEXT.md` reflects T072. | those files |
| EW-06 | Diff does not implement payments T040–T043, T004, Dependabot, WhatsApp templates, or retention docs. Domain/core coverage ≥ 95%. Ruff + import style pass. | whole diff |

## Builder report

After implementation, write `docs/specs/sdd/T072-builder-report.md`:

| ID | Result (`done` or `skipped`) | Files | What changed |
|----|-------------------------------|-------|----------------|

Add a **Files touched** list of every path in the diff and the exact test commands with results. The reviewer treats any path not justified by an ID as **extra**.

## Reviewer comparison

Read this file, the builder report, and the diff. Return only:

- One line per ID: `EW-xx match|gap — evidence`
- Extras: paths or behavior not in the table
- Bugs that break an ID
- Verdict: accept or reject

Do not implement.

## Related

- [CONTEXT.md](../../../CONTEXT.md)
- [T010-job-internal-secret-sdd.md](./T010-job-internal-secret-sdd.md)
- [threat-model.md](../../threat-model.md)
- [decision.md](../../decision.md)
- [COMMERCIAL-LAUNCH.md](../../COMMERCIAL-LAUNCH.md) item 19

## Revision history

| Date | Change |
|------|--------|
| 2026-11-18 | Initial SDD (T072 operator API auth) |
