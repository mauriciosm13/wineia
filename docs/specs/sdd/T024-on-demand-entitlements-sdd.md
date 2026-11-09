# SDD — Domain on-demand entitlements (T024)

**Status:** draft  
**Task:** [T024](../../ROADMAP-TASKS.md)

## Problem

Hardcoded DAILY_LIMIT=2 ignores plan_tier and mixes with scheduled sends.

## Goals

Tier-based daily on-demand caps in messaging_service; UTC daily_reset; separate from T012/T021.

## Acceptance criteria

ENTRY 2 / SUPERIOR 10 MVP defaults; on_demand_entitlements module; persistence on Customer.

## Related

- `domain/services/messaging_service.py`

## Revision history

| Date | Change |
|------|--------|
| 2026-11-10 | Initial SDD |
