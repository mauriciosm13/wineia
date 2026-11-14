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

**Rolling 7 days with a 6h grace:** a customer is eligible if `last_weekly_education_at` is missing or at least 7×24 hours minus `WEEKLY_EDUCATION_GRACE` (6h) before job run time (UTC). The grace exists because `last_weekly_education_at` is stamped after the Claude call, so next Monday's run can start a few seconds earlier than last week's stamp. Not tied to ISO calendar Monday–Sunday.

Field `last_weekly_education_at` is set on the customer entity when an education message is enqueued.

## Copy and fan-out

1. **One** `IAService.generate_weekly_education()` Claude call per job run (Portuguese didactic tip).
2. Same message body enqueued to Cloud Tasks `send_message` for each eligible phone (`enqueue_send_message`).

## Scheduler

CD creates the Cloud Scheduler job `wine-send-weekly-education`, which `POST`s this path every **Monday at 15:00 `America/Sao_Paulo`** (cron `0 15 * * 1`) with the internal secret header — see [DEPLOYMENT.md](../DEPLOYMENT.md#cloud-scheduler-jobs-created-by-cd) (T031). Manual `curl` with the same header still works.

## Related

- [customer-plan-tier.md](./customer-plan-tier.md) — opt-in field
- [ROADMAP-TASKS.md](../ROADMAP-TASKS.md) T023 — broader broadcast-slot polish
