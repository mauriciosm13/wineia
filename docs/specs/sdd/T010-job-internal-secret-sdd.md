# SDD — JOB_INTERNAL_SECRET middleware (T010)

**Status:** implemented  
**Task:** [T010](../../ROADMAP-TASKS.md)

## Problem

Forged POSTs to `/jobs/*` and `/workers/*` could trigger sends or jobs.

## Goals

`JOB_INTERNAL_SECRET` env + `X-Job-Internal-Secret` on callers; constant-time compare; 401 if missing.

## Acceptance criteria

Middleware on routes; Cloud Tasks header; documented in DEPLOYMENT and PRODUCTION.

## Related

- `api/internal_job_auth.py`
- `docs/DEPLOYMENT.md`

## Revision history

| Date | Change |
|------|--------|
| 2026-11-10 | Initial SDD |
