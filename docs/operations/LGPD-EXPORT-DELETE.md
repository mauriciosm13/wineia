# LGPD — Export and erase customer by phone

Operator tooling for commercial launch item **#62** (task **T051**). Spec: [T051-export-delete-tooling-sdd.md](../specs/sdd/T051-export-delete-tooling-sdd.md). Auth: **T072** — same `JOB_INTERNAL_SECRET` as jobs/workers.

## Auth (read first)

These paths live under `/customers*` and require header **`X-Job-Internal-Secret`** matching Cloud Run env `JOB_INTERNAL_SECRET`. Missing, wrong, or unset secret → **401**. Prefer calling from a trusted operator machine; do not paste the secret into tickets or chat logs.

## Export

Returns a JSON dump of customer PII fields (phone, name, plan fields, preferences, consent, counters) plus optional linked pre-sale (`whatsapp == phone`). No secrets.

```bash
SERVICE_URL="$(gcloud run services describe wine-concierge \
  --region southamerica-east1 --project wineia-490200 \
  --format='value(status.url)')"

# Load secret from Secret Manager (example id); do not echo it
SECRET="$(gcloud secrets versions access latest \
  --secret=wine-concierge-job-internal-secret --project=wineia-490200)"

# URL-encode "+" as %2B when needed
curl -sS -H "X-Job-Internal-Secret: $SECRET" \
  "$SERVICE_URL/customers/%2B5511999999999/export"
```

- `200` — export body
- `401` — missing/wrong/unset secret
- `404` — no Customer for that phone (pre-sale-only leads are not exported here)

## Erase (anonymize)

Anonymizes the Customer row in place and deletes a linked PreSaleCustomer when present. **Does not** hard-delete recommendation history or financial records (payments not implemented yet; retain until a retention policy says otherwise).

```bash
curl -sS -X POST -H "X-Job-Internal-Secret: $SECRET" \
  "$SERVICE_URL/customers/%2B5511999999999/erase"
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
- `401` — missing/wrong/unset secret
- `404` — no Customer for that phone

## Related

- [PRODUCTION.md](./PRODUCTION.md) — route table and security notes
- [DEPLOYMENT.md](../DEPLOYMENT.md#job_internal_secret-jobs-workers-and-operator-apis) — secret header
- [T072-operator-api-auth-sdd.md](../specs/sdd/T072-operator-api-auth-sdd.md)
- [COMMERCIAL-LAUNCH.md](../COMMERCIAL-LAUNCH.md) item 62
