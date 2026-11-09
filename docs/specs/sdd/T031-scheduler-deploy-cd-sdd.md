# SDD — Scheduler jobs in deploy/CD (T031)

**Status:** draft  
**Task:** [T031](../../ROADMAP-TASKS.md)

## Problem

Jobs exist but Scheduler/cron not provisioned in CD.

## Goals

Document and/or automate Cloud Scheduler HTTP targets for recommendation and education jobs with OIDC/secret header.

## Acceptance criteria

Jobs POST with X-Job-Internal-Secret; align region and SERVICE_URL; idempotent apply in deploy workflow or runbook.

## Related

- `docs/DEPLOYMENT.md`
- `docs/ROADMAP.md M5`

## Revision history

| Date | Change |
|------|--------|
| 2026-11-10 | Initial SDD |
