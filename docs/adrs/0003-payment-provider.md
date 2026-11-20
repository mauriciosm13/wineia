# ADR 0003: Payment provider

**Status:** Proposed (leaning **Asaas** — accept in **T040**)

**Context:** WineAI will sell tiered WhatsApp subscriptions in Brazil (see [commercial.md](../commercial.md)). Checkout is hosted (Instagram → Asaas link); Cloud Run activates tiers via webhooks ([T044](../specs/sdd/T044-asaas-payment-webhook-sdd.md)).

**Decision:** _Pending formal Accept in T040._ **Intent:** **Asaas** as primary provider (BR subscriptions, Pix/card, payment links, sandbox). Evaluation notes: [payments-evaluation.md](../payments-evaluation.md).

**Consequences:** Webhook route `POST /webhooks/asaas`; idempotency keys; subprocessors list (CL #63); LGPD DPA appendix; no custom card UI in MVP.

**Alternatives:** Mercado Pago, Stripe, PagBank — remain fallbacks if Asaas sandbox fails product needs.
