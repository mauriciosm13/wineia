# Payment API evaluation (Brazil)

**Status:** **Asaas chosen** (2026-11-15) — COMMERCIAL-LAUNCH #53 / T040.  
**Runner-up:** Mercado Pago.  
**ADR:** [adrs/0003-payment-provider.md](./adrs/0003-payment-provider.md) (Accepted).

**CNPJ:** available — use business accounts for Mercado Pago / Stripe / Asaas / PagBank sandboxes.

## Requirements

| Requirement | Why | Coverage note |
|-------------|-----|---------------|
| Recurring billing | Entry / Superior / add-on subscriptions | All four shortlist providers support subscriptions; Asaas and Stripe are strongest for SaaS-style recurrence |
| Webhooks + idempotency | Activate tier on pay; stop on cancel | All expose webhooks; implementers must key on provider event id (T042) |
| Pix + card | BR conversion and cost mix | Mercado Pago, Asaas, PagBank are native; Stripe BR needs careful method enablement |
| Sandbox | CI/staging spikes without prod money | All offer sandbox/test mode; ops must smoke Asaas before T042 |

## Scoring method

Weights (fixed): **cost 40%**, **ease 35%**, **recurrence 25%**.  
Each criterion scored **1–10**. Weighted total = `cost×0.40 + ease×0.35 + recurrence×0.25`.

Scores are directional for product decision. **Live MDR, Pix fees, and subscription pricing must be verified by ops against current commercial sheets before production cutover** — published list prices change and CNPJ negotiation matters.

## Scored comparison

| Provider | Cost (40%) | Ease (35%) | Recurrence (25%) | Weighted total |
|----------|------------|------------|------------------|----------------|
| **Asaas** | 8 | 8 | 10 | **8.50** |
| Mercado Pago | 7 | 9 | 7 | **7.70** |
| Stripe | 5 | 9 | 9 | **7.40** |
| PagBank | 7 | 6 | 5 | **6.15** |

### Score justifications

**Asaas (chosen — 8.50)**  
- **Cost (8):** Competitive for BR subscription SaaS with transparent Pix + card MDR; often cheaper than Stripe for local cards. Not marked 10 because live sheets and volume tiers need ops confirmation.  
- **Ease (8):** Portuguese docs, CNPJ-first onboarding, sandbox, and webhook model familiar to BR operators. Slightly behind Mercado Pago / Stripe on global DX polish.  
- **Recurrence (10):** Recurrence-first product (assinaturas / cobrança recorrente) aligned with Entry / Superior / education add-on. Strong fit for webhook-driven activate/cancel.  
- **Pix + card, webhooks, sandbox:** Native Pix and card; webhooks suitable for idempotent event handling; sandbox available under CNPJ.

**Mercado Pago (runner-up — 7.70)**  
- **Cost (7):** Solid Pix economics; card MDR varies by method/installments — verify live.  
- **Ease (9):** Highest BR brand familiarity, mature sandbox, strong docs and community.  
- **Recurrence (7):** Subscriptions exist but the platform is checkout/marketplace-heavy; more wiring for pure SaaS recurrence than Asaas.  
- **Fallback:** Prefer if Asaas KYC, pricing, or webhook reliability fails ops smoke.

**Stripe (7.40)**  
- **Cost (5):** Excellent DX but BR card/Pix fee mix is often worse for small local SaaS volumes.  
- **Ease (9):** Best developer experience and Billing APIs; CNPJ / BR tax setup is heavier than local PSPs.  
- **Recurrence (9):** Stripe Billing is world-class for subscriptions and idempotent webhooks.  
- **Pix + card:** Card-first globally; Pix support in BR must be confirmed for the exact account mode before relying on it.

**PagBank (6.15)**  
- **Cost (7):** Competitive consumer payments; SaaS subscription packaging less clear.  
- **Ease (6):** Docs and SaaS webhook patterns thinner than the other three.  
- **Recurrence (5):** Recurring billing exists but is not the primary product story for WineAI’s tier model.  
- Kept on shortlist for completeness; not preferred for T042.

## Decision

| Role | Provider | Next step |
|------|----------|-----------|
| **Chosen** | **Asaas** | Manual provisioning until T042; update subprocessors; LGPD DPA |
| Runner-up | Mercado Pago | Revisit only if Asaas fails ops verification |

### Ops prerequisite for T042 (not a T040 deliverable)

Before implementing payment webhooks:

1. Open an Asaas sandbox with the company CNPJ.
2. Create one test subscription (or recurring charge) and confirm one webhook delivery to a non-prod endpoint (signature verified, event id logged).
3. Spot-check current MDR / Pix / subscription fees against the scores above; escalate if fees invalidate the cost ranking.
4. Only then start T042 (`POST /webhooks/payments`).

## Process (completed for T040)

1. ~~Sandbox top 2 providers (CNPJ).~~ → Documented as **T042 ops prerequisite** (Asaas primary; Mercado Pago if needed).  
2. ~~One test subscription + one webhook in a dev project.~~ → Same ops gate; not executed in this docs task.  
3. Record winner in [adrs/0003-payment-provider.md](./adrs/0003-payment-provider.md). **Done — Asaas.**  
4. Mark COMMERCIAL-LAUNCH #53 complete; implement #56–#57 later (T042).

## Until webhooks (T042)

Manual provisioning via customer APIs + operator runbook (see COMMERCIAL-LAUNCH #55, #58; T043).
