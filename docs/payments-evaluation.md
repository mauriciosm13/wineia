# Payment API evaluation (Brazil)

**Status:** not chosen — complete before implementing webhooks (COMMERCIAL-LAUNCH #53).

**CNPJ:** available — use business accounts for Mercado Pago / Stripe / Asaas sandboxes.

## Requirements

| Requirement | Why |
|-------------|-----|
| Recurring billing | Entry / Superior / add-on subscriptions |
| Webhooks + idempotency | Activate tier on pay; stop on cancel |
| Pix + card | BR conversion and cost mix |
| Sandbox | CI/staging spikes without prod money |

## Shortlist

| Provider | Ease | Cost (verify live pricing) |
|----------|------|----------------------------|
| Mercado Pago | High in BR | MDR + Pix |
| Stripe | High DX | Compare BR fees |
| Asaas | Recurrence-focused | Often strong for subscriptions |

Score in a table (cost 40%, ease 35%, recurrence 25%) — copy template from wine-concierge planning if needed.

## Process

1. Sandbox top 2 providers (CNPJ).
2. One test subscription + one webhook in a dev project.
3. Record winner in [adrs/0003-payment-provider.md](./adrs/0003-payment-provider.md).
4. Mark COMMERCIAL-LAUNCH #53 complete; implement #56–#57.

## Until decided

Manual provisioning via customer APIs + operator runbook (see COMMERCIAL-LAUNCH #55, #58).
