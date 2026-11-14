# SPEC — T030 POST /workers/send-campaign

Implementation contract for the `wine-campaigns` worker. Sources: `CONTEXT.md`, `PLAN.md`, and `docs/specs/sdd/T030-send-campaign-worker-sdd.md`. Expected work IDs EW-01 through EW-09 are the reviewer's checklist. This spec does not add behavior those sources do not name.

## Problem

`core/queues.py` points `send_campaign` at `/workers/send-campaign` on queue `wine-campaigns`. `CloudTasksClient.enqueue` posts to that path and adds `X-Job-Internal-Secret` only when `JOB_INTERNAL_SECRET` is set. The router has no handler. Auth runs before lookup: a missing or wrong secret returns 401. A valid secret then 404s because the path is not in `ROUTES`.

`POST /workers/send-message` already accepts JSON `{"phone", "message"}`, calls the module-level Twilio `client.send_text`, and returns `200` with body `{"status":"sent"}`. Auth for every `/workers/` path is already in `path_requires_internal_job_auth`.

## Scope

- Register `POST /workers/send-campaign` in `api/routes.py`.
- Share one private parse-and-send function between `handle_send_message` and `handle_send_campaign` so the payload contract cannot drift.
- `handle_send_campaign` accepts the same JSON body as `handle_send_message` (`phone` and `message`), sends via the existing module-level Twilio client, and returns the same success response.
- Cover the existing `/workers/` internal-job auth prefix with a test. Do not add a second auth scheme.
- Unit tests with a fake or patched `send_text`. No Datastore and no live Twilio.
- Update operator docs that still say the campaign worker is missing, and mark only the T030 / M5 worker checkbox done.
- After EW-01–EW-07 and EW-09 hold, check T030 and commercial-launch item 26 and set the SDD and index status to `implemented`.
- Write `docs/specs/sdd/T030-builder-report.md` with one row per EW-01–EW-09 and a **Files touched** list of every path in the diff.

Implement on branch `feat/t030-send-campaign-worker` cut from `main`. Do not commit this work onto `feature/recon-planner`. Do not push.

## Out of scope

- T004 GitHub branch protection.
- T031 Cloud Scheduler in CD, and provisioning the `wine-campaigns` queue.
- T032 async webhook replies.
- T060 / T061 IA caps and global budget.
- Enqueueing a new campaign job. Nothing in the repo calls `enqueue("send_campaign", ...)` today. Do not invent a producer.
- Changing on-demand entitlements, recommendation cadence, or education jobs.
- Editing `docs/MVP_SCOPE.md`. It may keep calling full campaign automation post-MVP.
- New status codes that `handle_send_message` does not already return. Missing keys and bad JSON stay uncaught, as on the message worker.
- A second Twilio client or a domain-service rewrite of the worker.
- Changing `core/queues.py`. `send_campaign.worker_path` stays `/workers/send-campaign`. Do not add a `worker_path` assertion. No Expected work ID asks for one.
- A required name for the private helper. The sources do not name it.

## Expected behavior

1. `POST /workers/send-campaign` with header `X-Job-Internal-Secret` matching `JOB_INTERNAL_SECRET`.
2. Body is JSON with `phone` and `message` (same keys as `handle_send_message`).
3. One private function in `api/handlers/worker_handler.py` reads those keys from the WSGI body and calls the existing module-level `client.send_text(phone, message)`. `handle_send_message` and `handle_send_campaign(environ, start_response)` both call that function. `handle_send_campaign` does not construct a Twilio client.
4. Success is `200 OK`, `Content-Type: application/json`, body bytes `{"status":"sent"}` (the bytes `handle_send_message` already returns).
5. Missing or wrong secret returns `401` with body `{"error": "unauthorized"}` (space after the colon, same bytes as `reject_unauthorized_internal_job`: `[b'{"error": "unauthorized"}']`) from the existing router gate, before the handler runs, and does not call `send_text`.
6. Unknown paths stay `404` plain text. This path must not 404 once the secret is valid.
7. `ROUTES["/workers/send-campaign"]` is `handle_send_campaign`. The import of `handle_send_campaign` stays on the existing one-line import. No parentheses and no line continuation.

## Decisions already made

| Topic | Decision |
|-------|----------|
| Next task | T030. T004 is GitHub admin, not this activity. T060 stays later. |
| Contract | Mirror `handle_send_message`. Same keys, same Twilio call, same `200` body. |
| Auth | Prefix rule in `api/internal_job_auth.py` already covers `/workers/send-campaign`. |
| Client | Reuse `api/handlers/worker_handler.py` module-level `client`. Do not construct a second Twilio client. |
| Queue | `wine-campaigns` / `worker_path` already set. No queue-config change required unless a test is missing. Do not change `core/queues.py` and do not add a `worker_path` assertion. |
| Errors | Do not catch bad JSON or missing keys. Those stay uncaught, as on the message worker. |
| Branch | Implement on `feat/t030-send-campaign-worker` cut from `main`. Do not commit T030 onto `feature/recon-planner`. Do not push. |
| Review | Builder writes a change list keyed by Expected work IDs. Reviewer compares that list to the SDD and reports match, gap, or extra. Reviewer does not edit the SDD or the builder report. |
| Docs order | Set SDD and index status to `implemented` only after the code matches EW-01–EW-07 and EW-09. |

## Acceptance criteria

One criterion per Expected work ID. Each is testable.

- **EW-01.** When either worker handler runs, the system shall use one private function in `api/handlers/worker_handler.py` that reads `phone` and `message` from the WSGI body and calls `client.send_text`, and both `handle_send_message` and `handle_send_campaign` shall call that function.
- **EW-02.** When `POST /workers/send-campaign` is handled, `handle_send_campaign(environ, start_response)` shall exist, shall read `phone` and `message` and call `client.send_text` through the shared function, and shall not construct its own Twilio client.
- **EW-03.** When the shared send succeeds, the system shall respond `200 OK` with `Content-Type: application/json` and body bytes `{"status":"sent"}`.
- **EW-04.** The route table shall map `ROUTES["/workers/send-campaign"]` to `handle_send_campaign`, and the import in `api/routes.py` shall stay one line with no parentheses and no line continuation.
- **EW-05.** `path_requires_internal_job_auth("/workers/send-campaign")` shall be true. A `route_request` through the real `ROUTES` entry with a missing or wrong `X-Job-Internal-Secret` shall return `401` and body `[b'{"error": "unauthorized"}']` and shall not call `send_text`. A matching secret shall reach the handler, and the path shall not 404 once the secret is valid. The route test shall not patch `/workers/send-campaign` out of the table.
- **EW-06.** A unit test under `tests/unit/api/` shall patch `send_text`, post JSON `phone` and `message`, and assert both arguments, status `200 OK`, and body `[b'{"status":"sent"}']`. The test shall not use live Twilio or Datastore. Exit check for the touched tests: `pytest` for those tests, `ruff`, and `python quality/check_import_style.py`. If the domain/core coverage gate runs, it stays at or above 95%. This change stays in `api/` and tests.
- **EW-07.** `docs/DEPLOYMENT.md`, `docs/operations/PRODUCTION.md`, `README.md`, and `AGENTS.md` shall list `POST /workers/send-campaign` as present (`DEPLOYMENT.md` drops the "not yet implemented" mark; `PRODUCTION.md` adds the route to its route table; `AGENTS.md` lists it on the API surface). `docs/ROADMAP.md` shall check only `/workers/send-campaign`. The Scheduler checkbox stays open (`[ ]`). `docs/MVP_SCOPE.md` is not edited.
- **EW-08.** Only after EW-01–EW-07 and EW-09 hold, `docs/ROADMAP-TASKS.md` shall check T030, `docs/COMMERCIAL-LAUNCH.md` shall check item 26, `docs/specs/sdd/T030-send-campaign-worker-sdd.md` status shall be `implemented`, and the T030 row in `docs/specs/sdd/INDEX.md` shall be `implemented`.
- **EW-09.** The diff shall not add Cloud Scheduler or CD wiring, a producer that calls `enqueue("send_campaign", ...)`, webhook reply queueing, entitlement or recommendation-cadence or education-job changes, or a second Twilio client. `core/queues.py` `send_campaign.worker_path` shall stay `/workers/send-campaign`, and that file shall not be changed.

Builder report (required by the handoff, not an extra Expected work ID): `docs/specs/sdd/T030-builder-report.md` has one row per EW-01–EW-09 with result `done` or `skipped`, files, and what changed, plus a **Files touched** list of every path in the diff. A path that no ID justifies is extra for the reviewer.

## Relevant files

| File | Role |
|------|------|
| `api/handlers/worker_handler.py` | `handle_send_message`; add shared send + `handle_send_campaign` |
| `api/routes.py` | Route table; one-line import of `handle_send_campaign` |
| `api/internal_job_auth.py` | `/jobs/` and `/workers/` secret check; do not add a second scheme |
| `core/queues.py` | `send_campaign` → `/workers/send-campaign`; do not edit |
| `infrastructure/queue/cloud_tasks_client.py` | Already posts to `worker_path` with `X-Job-Internal-Secret`; do not add a producer |
| `docs/specs/sdd/T030-send-campaign-worker-sdd.md` | Expected-work checklist; status `implemented` only after the checklist holds |
| `docs/specs/sdd/INDEX.md` | T030 row status matches the SDD |
| `docs/specs/sdd/T030-builder-report.md` | One row per Expected work ID; written by the builder; reviewer does not edit it |
| `docs/DEPLOYMENT.md` | Remove the "not yet implemented" mark on the campaign worker |
| `docs/operations/PRODUCTION.md` | Add the route to the route table |
| `README.md` | List the route as present |
| `AGENTS.md` | List `POST /workers/send-campaign` on the API surface |
| `docs/ROADMAP.md` | Check only `/workers/send-campaign`; Scheduler stays open |
| `docs/ROADMAP-TASKS.md` | Check T030 |
| `docs/COMMERCIAL-LAUNCH.md` | Check item 26 |
| `tests/unit/api/test_internal_job_auth.py` | Assert the campaign path requires internal job auth |
| `tests/unit/api/` | Route test for 401 vs authorized handler; patched `send_text` success test |

## Implementation order

Follow `PLAN.md`. Do not flip EW-08 status before tasks 1–5 match EW-01–EW-07 and EW-09.

| # | Task | EW |
|---|------|----|
| 1 | Shared parse-and-send helper and `handle_send_campaign` | EW-01, EW-02, EW-03 |
| 2 | Register the route | EW-04 |
| 3 | Auth and handler tests | EW-05, EW-06 |
| 4 | Operator docs for the route | EW-07 |
| 5 | Confirm the diff stays inside EW-09 | EW-09 |
| 6 | Check T030 / item 26 and mark the SDD implemented | EW-08 |
| 7 | Builder report | EW-01–EW-09 |
