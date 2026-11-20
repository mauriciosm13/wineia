# SDD — Payment webhook handler (T042)

**Status:** draft  
**Task:** [T042](../../ROADMAP-TASKS.md) · Asaas detail [T044](./T044-asaas-payment-webhook-sdd.md)

## Problem

Provider events must activate/deactivate tier without trusting the client browser.

## Goals

- Provider-agnostic contract: verify authenticity; idempotent event id; map to `subscription_status` + `plan_tier`.
- Concrete first provider: **Asaas** via **T044** (`POST /webhooks/asaas`).
- Align with CL #56–#57.

## Acceptance criteria

Depends T040; threat model update; no secrets / PAN in logs; T044 implements Asaas specifics.

## Related

- [T044](./T044-asaas-payment-webhook-sdd.md) · `docs/COMMERCIAL-LAUNCH.md` #56–#57

## Revision history

| Date | Change |
|------|--------|
| 2026-11-10 | Initial SDD |
| 2026-11-20 | Point to Asaas T044; Instagram checkout → webhook activation |
