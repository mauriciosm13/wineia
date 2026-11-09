# SDD — `/workers/send-campaign` worker (T030)

**Status:** implemented  
**Task:** [T030](../ROADMAP-TASKS.md) · COMMERCIAL-LAUNCH [#26](../COMMERCIAL-LAUNCH.md) · ROADMAP [M5](../ROADMAP.md)  
**Depends on:** M5 partial wiring — `core/queues.py` queue `wine-campaigns`, `JOB_INTERNAL_SECRET` on `/workers/*` (T010)

## Why this document

Spec-Driven Document for **T030**: close the gap where Cloud Tasks queue **`wine-campaigns`** points at a worker path that **does not exist** in the API (`DEPLOYMENT.md`).

This task delivers the **worker HTTP endpoint only**. Scheduling, CD provisioning of Scheduler, and job endpoints that enqueue on `send_campaign` are **T031** / follow-ups unless explicitly added in the implementation PR.

## Problem

- `QUEUES["send_campaign"]` maps `wine-campaigns` → **`POST /workers/send-campaign`**.
- Today only **`/workers/send-message`** is registered; campaign queue deliveries would **404**.
- Separate queue exists for **lower throughput** (`rate_limit_per_second: 2` vs `5`) for bulk/campaign traffic.

## Goals

1. Implement **`POST /workers/send-campaign`** with the same **internal secret** gate as other `/workers/*` routes (middleware in `api/routes.py`).
2. Accept a JSON body and send WhatsApp text via the existing Twilio adapter (same integration pattern as `handle_send_message`).
3. Return **`200`** JSON `{"status": "sent"}` on success; **`400`** on invalid JSON or missing fields.
4. Unit tests for handler success and validation; route smoke test optional.
5. Update **PRODUCTION.md**, **COMMERCIAL-LAUNCH #26**, **ROADMAP-TASKS T030**, and set this SDD status to **implemented** when done.

## Non-goals (T030)

- Cloud Tasks **enqueue** from a new `/jobs/*` campaign orchestrator (future work may call `CloudTasksClient.enqueue("send_campaign", ...)`).
- Terraform/CD for queue creation (ops already documented).
- Campaign content model / segmentation beyond phone + message body.
- **T031** Scheduler in deploy/CD.

## HTTP contract (normative)

| Method | Path | Auth |
|--------|------|------|
| POST | `/workers/send-campaign` | Header `X-Job-Internal-Secret` (= `JOB_INTERNAL_SECRET`) |

### Request body

JSON object (UTF-8), **`Content-Type: application/json`**:

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `phone` | string | yes | E.164 or format accepted by Twilio client today |
| `message` | string | yes | Outbound body (Portuguese product copy) |

Optional future fields (`campaign_id`, `slot_id`) are **out of scope**; do not require them in T030.

### Responses

| Condition | Status | Body |
|-----------|--------|------|
| Valid auth + send OK | 200 | `{"status": "sent"}` |
| Missing/invalid JSON or missing `phone`/`message` | 400 | `{"error": "..."}` (consistent with existing handlers) |
| Missing/invalid secret | 401 | `{"error": "unauthorized"}` (middleware) |

## Behavior

1. Read `CONTENT_LENGTH`, parse JSON.
2. Validate `phone` and `message` present (non-empty strings).
3. Call `create_twilio_whatsapp_client()` (or shared client pattern from `handle_send_message`) → `send_text(phone, message)`.
4. No domain business rules in the handler (Clean Architecture: HTTP only).

**Idempotency:** Cloud Tasks may retry; duplicate sends are acceptable for MVP (document in ops). No dedup store in T030.

## Queue alignment

- Producers (future jobs) call `CloudTasksClient.enqueue("send_campaign", {"phone": "...", "message": "..."})`.
- Client must set worker URL to `SERVICE_URL + "/workers/send-campaign"` and attach `X-Job-Internal-Secret` when configured (existing client behavior).

## Security

- Same threat model as `/workers/send-message` — [threat-model.md](../threat-model.md).
- Worker must remain **non-public** in practice: secret required when `JOB_INTERNAL_SECRET` is set.

## Acceptance tests (implementer checklist)

| # | Case | Expect |
|---|------|--------|
| 1 | Valid payload + mocked Twilio | 200, `status: sent`, `send_text` called once |
| 2 | Missing `phone` | 400 |
| 3 | Missing `message` | 400 |
| 4 | Invalid JSON | 400 |
| 5 | Route registered | `POST /workers/send-campaign` reaches handler (integration-style unit test if pattern exists) |
| 6 | Without secret when env set | 401 (reuse existing internal auth tests pattern) |

## Rollout / ops

- After deploy, verify queue `wine-campaigns` OIDC/target URL points to this path (manual; **T031**).
- Until a job enqueues `send_campaign`, endpoint is idle but **reachable** for manual curl tests with secret header.

## Related

- [weekly-education-job.md](./weekly-education-job.md) — job + fan-out pattern
- [recommendation-broadcast-slot.md](./recommendation-broadcast-slot.md) — shared copy
- `api/handlers/worker_handler.py` — reference implementation

## Revision history

| Date | Change |
|------|--------|
| 2026-11-10 | Initial SDD (T030) |
