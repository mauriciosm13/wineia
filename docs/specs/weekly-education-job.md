# Spec — Weekly education job (T022)

## Purpose

Send one **didactic** WhatsApp message per week to customers who opted in via `weekly_education_opt_in`. Aligns with [commercial.md](../commercial.md) education add-on and COMMERCIAL-LAUNCH #25.

## Endpoint

| Method | Path | Auth |
|--------|------|------|
| POST | `/jobs/send-weekly-education` | Header `X-Job-Internal-Secret` (= `JOB_INTERNAL_SECRET`) |

Response: `200` JSON `{"status": "ok"}` on success (same pattern as `/jobs/send-recommendations`).

## Cohort

- `status == active`
- `weekly_education_opt_in == true`

## Cadence

**Rolling 7 days:** a customer is eligible if `last_weekly_education_at` is missing or at least 7×24 hours before job run time (UTC). Not tied to ISO calendar Monday–Sunday.

Field `last_weekly_education_at` is set on the customer entity when an education message is enqueued.

## Copy and fan-out

1. **One** `IAService.generate_weekly_education()` Claude call per job run (Portuguese didactic tip).
2. Same message body enqueued to Cloud Tasks `send_message` for each eligible phone (`enqueue_send_message`).

## Scheduler

Operator configures Cloud Scheduler (or manual `curl`) to `POST` this path weekly with the internal secret header — see [DEPLOYMENT.md](../DEPLOYMENT.md).

## Related

- [customer-plan-tier.md](./customer-plan-tier.md) — opt-in field
- [ROADMAP-TASKS.md](../ROADMAP-TASKS.md) T023 — broader broadcast-slot polish
