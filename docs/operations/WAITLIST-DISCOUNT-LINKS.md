# Waitlist — discount Asaas links (ops runbook)

Manual MVP for **T088** after leads are captured via public `POST /waitlist`. Automated WhatsApp send of checkout links is out of scope.

## List / export leads

Requires `JOB_INTERNAL_SECRET` (same header as other operator APIs).

```bash
curl -sS -H "X-Job-Internal-Secret: $JOB_INTERNAL_SECRET" \
  "$SERVICE_URL/waitlist"
```

Response shape: `{"leads":[...],"count":N}` with phone, name, email, birth_date, created_at, updated_at.

## Send discounted checkout (manual)

1. Export leads from `GET /waitlist`.
2. In Asaas, create payment/checkout links with the campaign discount for each lead (or a batch).
3. Send the link to the lead via WhatsApp or email (ops-owned channel). Prefer the waitlist WhatsApp `phone`.
4. Track sent links outside the product for now (spreadsheet OK). Optional fields `checkout_sent_at` / `discount_code` are not in the API yet.

## Distinction vs pre-sale

| | Waitlist (`/waitlist`) | Pre-sale (`/customers/pre-sale`) |
|--|------------------------|----------------------------------|
| Who creates | Public frontend (rate-limited) | Operator with job secret |
| Purpose | Launch pré-lista → discount checkout later | Operator funnel → activate Customer |

Do **not** replace pre-sale with waitlist.

## LGPD

Waitlist PII is inventoried in [DATA-RETENTION.md](./DATA-RETENTION.md). Export/erase for waitlist-only leads is a follow-up; until then treat `GET /waitlist` as internal-only and minimize copies.
