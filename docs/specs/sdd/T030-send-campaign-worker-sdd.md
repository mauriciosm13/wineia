# SDD — POST /workers/send-campaign (T030)

**Status:** implemented  
**Task:** [T030](../../ROADMAP-TASKS.md)  
**Comparison contract:** this Expected work list is what the reviewer checks against [T030-builder-report.md](./T030-builder-report.md).

## Problem

`core/queues.py` points `send_campaign` at `/workers/send-campaign` on queue `wine-campaigns`. `CloudTasksClient.enqueue` posts to that path and adds `X-Job-Internal-Secret` only when `JOB_INTERNAL_SECRET` is set. The router has no handler. Auth runs before lookup: a missing or wrong secret returns 401. A valid secret then 404s because the path is not in `ROUTES`.

`POST /workers/send-message` already accepts JSON `{"phone", "message"}`, calls `client.send_text`, and returns `200` `{"status":"sent"}`. Auth for every `/workers/` path is already in `path_requires_internal_job_auth`.

## Goals

- Add the campaign worker with the same payload, Twilio call, and success body as the message worker.
- One shared function owns that contract so the two routes cannot diverge.
- Document the route and mark only the T030 / M5 worker checkbox done.

## Non-goals

- Cloud Scheduler in deploy/CD (T031).
- Moving webhook replies onto a queue (T032).
- Creating the `wine-campaigns` queue in GCP.
- A new job that enqueues `send_campaign`.
- New error statuses. `handle_send_message` does not catch bad JSON or missing keys; the campaign worker must not invent that behavior.
- A second Twilio client or a domain-service rewrite of the worker.
- `docs/MVP_SCOPE.md`. It may keep calling full campaign automation post-MVP.

## Behavior

1. `POST /workers/send-campaign` with header `X-Job-Internal-Secret` matching `JOB_INTERNAL_SECRET`.
2. Body is JSON with `phone` and `message` (same keys as `handle_send_message`).
3. The handler calls the module-level Twilio `client.send_text(phone, message)`.
4. Response is `200`, `Content-Type: application/json`, body `{"status":"sent"}`.
5. Missing or wrong secret returns `401` with body `{"error": "unauthorized"}` (space after the colon, same bytes as `reject_unauthorized_internal_job`) from the existing router gate, before the handler runs.
6. Unknown paths stay `404` plain text. This path must not 404 once the secret is valid.

## Expected work

The builder implements only these items. The reviewer marks each **match**, **gap**, or **extra**.

| ID | Must be true when the work is done | Where |
|----|--------------------------------------|--------|
| EW-01 | One private function reads `phone` and `message` from the WSGI body and calls `client.send_text`. `handle_send_message` and `handle_send_campaign` both call it. | `api/handlers/worker_handler.py` |
| EW-02 | `handle_send_campaign(environ, start_response)` exists and does not construct its own Twilio client. | `api/handlers/worker_handler.py` |
| EW-03 | Success is `200 OK` and body bytes `{"status":"sent"}`. | `api/handlers/worker_handler.py` |
| EW-04 | `ROUTES` maps `/workers/send-campaign` to `handle_send_campaign`. Import stays one line, no parentheses. | `api/routes.py` |
| EW-05 | `path_requires_internal_job_auth("/workers/send-campaign")` is true. A routed request without the secret returns 401 and does not call `send_text`. A routed request with the secret calls the handler. | `tests/unit/api/test_internal_job_auth.py` and a route test |
| EW-06 | Unit test patches `send_text`, posts `phone` + `message`, and asserts both arguments plus status and body. No live Twilio and no Datastore. | `tests/unit/api/` |
| EW-07 | Docs name the route as implemented. `ROADMAP.md` checks only `/workers/send-campaign`. Scheduler stays `[ ]`. | `docs/DEPLOYMENT.md`, `docs/operations/PRODUCTION.md`, `README.md`, `AGENTS.md`, `docs/ROADMAP.md` |
| EW-08 | T030 and commercial-launch item 26 are checked. This SDD status becomes `implemented` only when EW-01–EW-07 and EW-09 hold. Index status matches. | `docs/ROADMAP-TASKS.md`, `docs/COMMERCIAL-LAUNCH.md`, `docs/specs/sdd/INDEX.md`, this file |
| EW-09 | Diff does not add Scheduler, a campaign producer, webhook queueing, entitlement changes, or a second Twilio client. `core/queues.py` `send_campaign.worker_path` stays `/workers/send-campaign`. | whole diff |

## Builder report

After implementation, write `docs/specs/sdd/T030-builder-report.md` with one row per ID:

| ID | Result (`done` or `skipped`) | Files | What changed |
|----|-------------------------------|-------|----------------|

Add a **Files touched** list of every path in the diff. The reviewer treats any path not justified by an ID as **extra**.

## Reviewer comparison

Read this file and the builder report. Return only:

- One line per ID: `EW-xx match|gap — evidence`
- Extras: paths or behavior not in the table
- Bugs that break an ID

Do not implement.

## Related

- `core/queues.py`
- `infrastructure/queue/cloud_tasks_client.py`
- `api/internal_job_auth.py`
- `docs/DEPLOYMENT.md`
- [CONTEXT.md](../../../CONTEXT.md)

## Revision history

| Date | Change |
|------|--------|
| 2026-11-10 | Initial stub |
| 2026-11-13 | Orchestrator checklist for reviewer comparison (EW-01–EW-09). 401 body matches the spaced JSON the gate already returns. |
