# SDD — Asaas payment webhook reception (T044)

**Status:** draft  
**Task:** [T044](../../ROADMAP-TASKS.md) · parent payments epic (T040–T043) · depends **T040** (Asaas chosen) + **T041** (subscription fields)

## Problem

WineAI must activate / revoke `plan_tier` when Asaas reports a successful payment or subscription lifecycle change. Instagram and site checkout go **direct to Asaas**; the product backend only learns about pay via **webhooks**.

## Goals

1. Document and implement `POST /webhooks/asaas` (or `/webhooks/payments/asaas`) on Cloud Run.
2. Verify authenticity (Asaas access token / webhook auth header — confirm in Asaas docs at implement time).
3. Idempotent processing by Asaas `event` + payment/subscription id (persist processed event ids).
4. Map liquidated payment / active subscription → Customer `subscription_status=ACTIVE` + correct `plan_tier` (ENTRY/SUPERIOR).
5. Map overdue / canceled / refunded (as product rules define) → `PAST_DUE` / `CANCELED` and stop paid entitlements.
6. Fail closed: invalid signature → 401/403; duplicate event → 200 no-op; unknown customer → log + alert path (manual T043 until matching rules exist).
7. Never log full payloads with card data; store only ids + status needed for ops.

## Non-goals

- Building a custom card form (checkout stays on Asaas).
- Full reconciliation UI.
- Hotmart / other providers in this slice.

## Proposed flow

```
Asaas (checkout / subscription)
  → HTTP webhook POST /webhooks/asaas
  → verify auth
  → idempotency check (event id)
  → resolve Customer by phone/email/externalReference
  → update subscription_status + plan_tier
  → 200 OK (fast; heavy work sync OK for MVP if < few hundred ms)
```

### Event families to support (confirm names in Asaas docs)

| Family | Product action (draft) |
|--------|------------------------|
| Payment confirmed / received | Activate or renew tier |
| Payment overdue / unpaid | `PAST_DUE`; soft-limit IA if policy says so |
| Subscription canceled / deleted | `CANCELED`; drop to free/none per commercial.md |
| Refund / chargeback | Revoke paid tier; ops note |

Exact Asaas event strings are pinned in Expected Work when sandbox is available.

### Customer matching

Prefer `externalReference` (or similar) set when creating the Asaas charge/subscription = WineAI phone E.164. Fallback: email on Customer / waitlist / pre-sale. Unmatched → do not invent a customer; queue for T043 manual provisioning.

## Current anchors

| Area | File / note |
|------|-------------|
| No payment webhook yet | `api/routes.py` |
| Tier field | `plan_tier` on Customer (T020) |
| Operator auth | Job secret on `/customers*` — **webhook must use Asaas auth, not job secret** |
| Threat model | Add Asaas webhook abuse / spoofing |

## Expected work

| ID | Work |
|----|------|
| EW-01 | Sandbox: create test subscription + capture real webhook payload samples in `docs/specs/` (redacted) |
| EW-02 | Domain service: apply payment event → subscription fields (pure; unit tested) |
| EW-03 | HTTP handler + signature/token verify; idempotent store |
| EW-04 | PRODUCTION / DEPLOYMENT / threat-model / subprocessors (CL #63) |
| EW-05 | Wire Asaas webhook URL to Cloud Run after deploy |

## Acceptance criteria

- [ ] Spec + tests for happy path activate + idempotent replay
- [ ] Docs for operators to register webhook URL in Asaas console
- [ ] Depends on T040 ADR Accepted (Asaas)

## Related

- [T040](./T040-payments-evaluation-adr-sdd.md) · [T041](./T041-subscription-state-fields-sdd.md) · [T042](./T042-payment-webhook-handler-sdd.md) · [T043](./T043-manual-provisioning-runbook-sdd.md)
- [payments-evaluation.md](../payments-evaluation.md) · [ADR 0003](../adrs/0003-payment-provider.md)
- Asaas API docs: https://docs.asaas.com · Sandbox: https://sandbox.asaas.com

## Revision history

| Date | Change |
|------|--------|
| 2026-11-20 | Initial draft — Instagram → Asaas checkout; webhook-only activation |
