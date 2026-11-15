# ADR 0003: Payment provider

**Status:** Accepted  
**Date:** 2026-11-15  
**Deciders:** WineAI team (parent defaults recorded in CONTEXT)  
**Related:** T040 · [COMMERCIAL-LAUNCH.md](../COMMERCIAL-LAUNCH.md) #53 · [payments-evaluation.md](../payments-evaluation.md) · [T040 SDD](../specs/sdd/T040-payments-evaluation-adr-sdd.md)

---

## Context

WineAI will sell tiered WhatsApp subscriptions in Brazil (see [commercial.md](../commercial.md)): Entry, Superior, and an education add-on. Activation and cancellation must eventually come from a payment provider webhook (T042). Until a provider is chosen, COMMERCIAL-LAUNCH #53 blocks that work and operators activate tiers manually via the customer API.

Requirements: recurring billing, webhooks with idempotent event ids, Pix + card, and a sandbox usable under the company CNPJ. Shortlist and scores live in [payments-evaluation.md](../payments-evaluation.md) (weights: cost 40%, ease 35%, recurrence 25%).

## Decision

1. **Use Asaas** as the payment provider for WineAI subscriptions.
2. **Mercado Pago is the runner-up** if Asaas onboarding, pricing, or webhook reliability fails ops verification.
3. **No payment webhook code in T040.** Route shape, signature verification, and idempotency keys are deferred to T042.
4. **Manual provisioning continues** (customer API + runbook T043 / CL #55) until T042 lands.
5. **Sandbox smoke is an ops prerequisite for T042**, not a T040 deliverable: one Asaas test subscription + one webhook delivery in a non-prod project, plus live MDR/fee spot-check before production cutover.

## Consequences

### Positive

- Clear #53 gate: T042 can design against Asaas webhooks
- Recurrence-first BR SaaS fit for Entry / Superior / add-on
- Subprocessors and LGPD paperwork can name a concrete vendor

### Negative / follow-ups

- **Webhook route shape deferred to T042** (`POST /webhooks/payments` or Asaas-specific path; signature + idempotent event id)
- **Subprocessors list** must name Asaas (started in `commercial.md`; CL #63 still tracks LGPD appendix completeness)
- **LGPD DPA** with Asaas must be executed before production payment data flows
- **Manual provisioning** remains the only activation path until T042
- Live fees may differ from the evaluation scores; ops must re-verify before cutover

### Neutral

- Stripe and PagBank stay documented alternatives; no integration work planned unless Asaas and Mercado Pago both fail

## Alternatives

| Alternative | Why not chosen |
|-------------|----------------|
| Mercado Pago (runner-up) | Strong BR ease and Pix; recurrence is secondary to checkout — more wiring for SaaS tiers. Keep as fallback. |
| Stripe | Best Billing DX and recurrence APIs; weaker cost position for BR Pix/card mix and heavier CNPJ/tax setup for this stage. |
| PagBank | Competitive consumer payments; thinner SaaS recurrence and webhook DX for WineAI’s model. |
| Manual-only forever | Blocks automated renewals and cancel; acceptable only as a temporary launch waiver, not the steady state. |

## References

- [payments-evaluation.md](../payments-evaluation.md)
- [COMMERCIAL-LAUNCH.md](../COMMERCIAL-LAUNCH.md) Phase 6
- [T042 SDD](../specs/sdd/T042-payment-webhook-handler-sdd.md)
