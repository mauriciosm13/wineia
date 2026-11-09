# SDD — Payment webhook handler (T042)

**Status:** draft  
**Task:** [T042](../../ROADMAP-TASKS.md)

## Problem

Provider events must activate/deactivate tier.

## Goals

POST /webhooks/payments (provider-specific); verify signature; idempotent event id; map to plan_tier.

## Acceptance criteria

Depends T040; threat model update; no secrets in logs.

## Related

- `docs/COMMERCIAL-LAUNCH.md #56`

## Revision history

| Date | Change |
|------|--------|
| 2026-11-10 | Initial SDD |
