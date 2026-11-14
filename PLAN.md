# PLAN — T030 POST /workers/send-campaign

Source of truth: `CONTEXT.md`, Expected work EW-01–EW-09 in `docs/specs/sdd/T030-send-campaign-worker-sdd.md`, and the recon summary. Branch `feat/t030-send-campaign-worker` from `main` is the implementer's step, not a task here. No commit and no push.

## Order

| # | Task | EW | Depends on |
|---|------|----|------------|
| 1 | Shared parse-and-send helper and `handle_send_campaign` | EW-01, EW-02, EW-03 | — |
| 2 | Register the route | EW-04 | 1 |
| 3 | Auth and handler tests | EW-05, EW-06 | 1, 2 |
| 4 | Operator docs for the route | EW-07 | 3 |
| 5 | Confirm the diff stays inside EW-09 | EW-09 | 1–4 |
| 6 | Check T030 / item 26 and mark the SDD implemented | EW-08 | 5 |
| 7 | Builder report | EW-01–EW-09 | 6 |

## Tasks

### 1. Shared helper and campaign handler (EW-01, EW-02, EW-03)

File: `api/handlers/worker_handler.py`.

- Extract one private function that reads `phone` and `message` from the WSGI body and calls the existing module-level `client.send_text`.
- `handle_send_message` and `handle_send_campaign(environ, start_response)` both call that function.
- `handle_send_campaign` does not construct a Twilio client.
- Success stays `200 OK`, `Content-Type: application/json`, body bytes `{"status":"sent"}` (the bytes `handle_send_message` already returns).
- Do not catch bad JSON or missing keys. Those stay uncaught, as on the message worker.

### 2. Register the route (EW-04)

File: `api/routes.py`.

- `ROUTES["/workers/send-campaign"]` is `handle_send_campaign`.
- Import `handle_send_campaign` on the existing one-line import. No parentheses and no line continuation.

### 3. Auth and handler tests (EW-05, EW-06)

- In `tests/unit/api/test_internal_job_auth.py`, assert `path_requires_internal_job_auth("/workers/send-campaign")` is true.
- Add a route test under `tests/unit/api/` that calls `route_request` with the real `ROUTES` entry (do not patch `/workers/send-campaign` out of the table):
  - Missing or wrong `X-Job-Internal-Secret` returns `401` and body `[b'{"error": "unauthorized"}']` (space after the colon) and does not call `send_text`.
  - A matching secret reaches the handler. The path must not 404 once the secret is valid.
- Add a unit test under `tests/unit/api/` that patches `send_text`, posts JSON `phone` and `message`, and asserts both arguments, status `200 OK`, and body `[b'{"status":"sent"}']`. No live Twilio and no Datastore.
- Exit check for this task: `pytest` for the touched tests, `ruff`, and `python quality/check_import_style.py`. If the domain/core coverage gate runs, it stays at or above 95%. This change stays in `api/` and tests.

### 4. Operator docs (EW-07)

State that `POST /workers/send-campaign` is present. Do not edit `docs/MVP_SCOPE.md`.

| File | Change |
|------|--------|
| `docs/DEPLOYMENT.md` | Remove the "not yet implemented" mark on the campaign worker. |
| `docs/operations/PRODUCTION.md` | Add the route to the route table. |
| `README.md` | List the route as present. |
| `AGENTS.md` | List `POST /workers/send-campaign` on the API surface. |
| `docs/ROADMAP.md` | Check only `/workers/send-campaign`. Leave the Scheduler checkbox open. |

### 5. EW-09 diff check (EW-09)

Before any status flip, confirm the diff does not add:

- Cloud Scheduler or CD wiring (T031)
- A producer that calls `enqueue("send_campaign", ...)`
- Webhook reply queueing (T032)
- Entitlement, recommendation-cadence, or education-job changes
- A second Twilio client

`core/queues.py` `send_campaign.worker_path` stays `/workers/send-campaign`. Do not change that file. Do not add a `worker_path` assertion; no Expected work ID asks for one. Do not provision queues.

### 6. Checklists and SDD status (EW-08)

Do this only after tasks 1–5 match EW-01–EW-07 and EW-09.

| File | Change |
|------|--------|
| `docs/ROADMAP-TASKS.md` | Check T030. |
| `docs/COMMERCIAL-LAUNCH.md` | Check item 26. |
| `docs/specs/sdd/T030-send-campaign-worker-sdd.md` | Set status to `implemented`. |
| `docs/specs/sdd/INDEX.md` | Set the T030 row to `implemented`. |

### 7. Builder report

Write `docs/specs/sdd/T030-builder-report.md` with one row per EW-01–EW-09:

| ID | Result (`done` or `skipped`) | Files | What changed |
|----|-------------------------------|-------|----------------|

Add a **Files touched** list of every path in the diff. A path that no ID justifies is extra for the reviewer.

## Open questions

None. CONTEXT.md already decided the contract, auth, client, queue path, error behavior, doc scope, and branch.
