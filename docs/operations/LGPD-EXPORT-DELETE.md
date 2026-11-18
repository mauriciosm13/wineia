# LGPD — Export and erase customer by phone

Operator tooling for commercial launch item **#62** (task **T051**). Spec: [T051-export-delete-tooling-sdd.md](../specs/sdd/T051-export-delete-tooling-sdd.md).

## Auth risk (read first)

These paths live under the existing `/customers*` API. Like `GET/POST/PATCH /customers`, they have **no application auth** and no `X-Job-Internal-Secret`. Treat them as **internal / operator-only**. Do not expose the Cloud Run URL publicly beyond what production already allows for customer CRUD. Prefer calling from a trusted operator machine with the production service URL.

## Export

Returns a JSON dump of customer PII fields (phone, name, plan fields, preferences, consent, counters) plus optional linked pre-sale (`whatsapp == phone`). No secrets.

```bash
SERVICE_URL="$(gcloud run services describe wine-concierge \
  --region southamerica-east1 --project wineia-490200 \
  --format='value(status.url)')"

# URL-encode "+" as %2B when needed
curl -sS "$SERVICE_URL/customers/%2B5511999999999/export"
```

- `200` — export body
- `404` — no Customer for that phone (pre-sale-only leads are not exported here)

## Erase (anonymize)

Anonymizes the Customer row in place and deletes a linked PreSaleCustomer when present. **Does not** hard-delete recommendation history or financial records (payments not implemented yet; retain until a retention policy says otherwise).

```bash
curl -sS -X POST "$SERVICE_URL/customers/%2B5511999999999/erase"
```

### What changes

| Entity | Action |
|--------|--------|
| Customer | `name` → `REDACTED`; `preferences` → `[]`; `status` → `canceled`; `weekly_education_opt_in` → `false`; consent fields cleared. Phone key kept. `plan` / `plan_tier` and operational counters retained. |
| PreSaleCustomer | Deleted when `whatsapp` matches the phone (email is the Datastore key; deleting removes the email key). |
| Recommendation history | **Not** deleted. |
| Financial / payment records | **Not** deleted (none in product yet). |

Response includes the anonymized customer fields plus `erased: true` and `pre_sale_deleted` (bool).

- `200` — erase completed
- `404` — no Customer for that phone

## Related

- [PRODUCTION.md](./PRODUCTION.md) — route table and security notes
- [COMMERCIAL-LAUNCH.md](../COMMERCIAL-LAUNCH.md) item 62
