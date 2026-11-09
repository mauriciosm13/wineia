# SDD — Secret Manager migration plan (T011)

**Status:** implemented  
**Task:** [T011](../../ROADMAP-TASKS.md)

## Problem

Long-lived secrets in env files risk leakage.

## Goals

Document inventory, IAM, phased Cloud Run secret refs; ADR 0004.

## Acceptance criteria

SECRET-MANAGER-MIGRATION.md + ADR 0004; no mandatory SDK in app phase 1.

## Related

- `docs/operations/SECRET-MANAGER-MIGRATION.md`
- `docs/adrs/0004-secret-manager-runtime-secrets.md`

## Revision history

| Date | Change |
|------|--------|
| 2026-11-10 | Initial SDD |
