# SDD — Domain on-demand entitlements (T024)

**Status:** Implemented (MVP)  
**Task:** [T024](../../ROADMAP-TASKS.md)

**Canonical detail:** [on-demand-entitlements-sdd.md](../on-demand-entitlements-sdd.md)

## Problem

Hardcoded `DAILY_LIMIT=2` ignored `plan_tier` and was not documented separately from scheduled sends or webhook abuse limits (T012).

## Goals

Tier-based daily on-demand caps in `messaging_service`; UTC `daily_reset` on the read path; separate from T012/T021.

## Acceptance criteria

- [x] ENTRY 2 / SUPERIOR 10 MVP defaults in `domain/on_demand_entitlements.py`
- [x] `messages_sent_today` + `daily_reset` on Customer; increment on successful IA reply
- [x] Unit tests for entitlements module and messaging paths

## Related

- `domain/services/messaging_service.py`
- [threat-model.md](../../threat-model.md) — product entitlements vs webhook rate limits

## Revision history

| Date | Change |
|------|--------|
| 2026-11-10 | Initial SDD |
| 2026-11-10 | Implemented; detail spec is canonical |
