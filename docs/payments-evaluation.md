# Payment API evaluation (Brazil)

**Status:** leaning **Asaas** (2026-11-20) — finalize ADR 0003 in **T040** before webhooks (**T044**).

**CNPJ:** available — use business accounts for Asaas sandbox.

## Product checkout shape

- Instagram / paid traffic → **direct Asaas checkout** (minimize drop-off).
- Optional WineAI site / waitlist form → later **discounted** Asaas payment links (T085–T088).
- WineAI Cloud Run does **not** host card forms; activation is **webhook-driven** (T044).

## Requirements

| Requirement | Why |
|-------------|-----|
| Recurring billing | Entry / Superior subscriptions |
| Webhooks + idempotency | Activate tier on pay; stop on cancel |
| Pix + card | BR conversion and cost mix |
| Sandbox | CI/staging spikes without prod money |
| Hosted checkout / payment links | Instagram deep-link without custom PCI UI |

## Shortlist

| Provider | Ease | Notes (verify live pricing) |
|----------|------|-----------------------------|
| **Asaas** (preferred) | High for BR subscriptions | Sales contact: no adesão/mensalidade; charge on success; web + API; sandbox + docs |
| Mercado Pago | High in BR | MDR + Pix |
| Stripe | High DX | Compare BR fees / checkout |
| PagBank / others | Medium | Fallback if Asaas sandbox fails product needs |

### Asaas pointers (from vendor)

| Resource | URL |
|----------|-----|
| Pricing | https://asaas.com/precos-e-taxas |
| Create account | https://www.asaas.com/onboarding/createAccount |
| API docs | https://docs.asaas.com |
| Sandbox | https://sandbox.asaas.com |
| Integrations support | integracoes@asaas.com.br |

## Process

1. Create Asaas sandbox account; one test subscription + webhook to a tunnel/Cloud Run.
2. Record event payload samples (redacted) under T044 EW-01.
3. Accept [ADR 0003](./adrs/0003-payment-provider.md) with **Asaas**.
4. Implement T041 → T044 → T043 as needed; mark COMMERCIAL-LAUNCH #53–#57.

## Until webhooks live

Manual provisioning via customer APIs + operator runbook (T043 / CL #55).
