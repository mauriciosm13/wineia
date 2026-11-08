# Spec — Recommendation broadcast slot (T023)

## Purpose

Scheduled recommendation sends for ENTRY/SUPERIOR must follow [commercial.md](../commercial.md) **shared copy**: one Claude generation per job slot, same body fan-out to all eligible phones.

## Endpoint

| Method | Path | Auth |
|--------|------|------|
| POST | `/jobs/send-recommendations` | Header `X-Job-Internal-Secret` (= `JOB_INTERNAL_SECRET`) |

## Slot flow (`send_recommendations`)

1. List active customers (`DatastoreCustomerRepository.list_active`).
2. **Select wine** — `select_wine()` (rotation / catalog rules unchanged).
3. Update content `last_sent` for the chosen wine.
4. **One** `IAService.generate_recommendation(wine=wine)` — Portuguese weekly recommendation for the slot. Per-customer `preferences` are **not** passed (broadcast copy is identical for the cohort).
5. For each customer: apply status, tier (`tier_gets_scheduled_recommendations`), and cadence (`should_send_scheduled_recommendation`); enqueue `send_message` with the **same** body; `record_scheduled_recommendation_send` + repository update.

## Cadence

Unchanged from [entry-recommendation-cadence-sdd.md](./entry-recommendation-cadence-sdd.md): max **2** sends per rolling **168h** for ENTRY/SUPERIOR.

## Related

- [weekly-education-job.md](./weekly-education-job.md) — same one-call + fan-out pattern for education
- COMMERCIAL-LAUNCH #24 · ROADMAP-TASKS T023
