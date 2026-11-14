# T030 builder report

Branch: `feat/t030-send-campaign-worker` (from `main`). Not committed. Not pushed.

| ID | Result (`done` or `skipped`) | Files | What changed |
|----|-------------------------------|-------|----------------|
| EW-01 | done | `api/handlers/worker_handler.py` | Added private `_send_worker_payload`. It reads `phone` and `message` from the WSGI body and calls the module-level `client.send_text`. `handle_send_message` and `handle_send_campaign` both return that helper. |
| EW-02 | done | `api/handlers/worker_handler.py` | Added `handle_send_campaign(environ, start_response)`. It uses the shared helper and does not construct a Twilio client. |
| EW-03 | done | `api/handlers/worker_handler.py` | Success stays `200 OK`, `Content-Type: application/json`, body bytes `{"status":"sent"}`. Bad JSON and missing keys stay uncaught. |
| EW-04 | done | `api/routes.py` | `ROUTES["/workers/send-campaign"]` is `handle_send_campaign`. Import is one line: `from api.handlers.worker_handler import handle_send_campaign, handle_send_message`. |
| EW-05 | done | `tests/unit/api/test_internal_job_auth.py`, `tests/unit/api/test_send_campaign_worker.py` | Path predicate asserts `/workers/send-campaign` requires internal job auth. Route tests use the real `ROUTES` entry. Missing or wrong secret returns `401` and `[b'{"error": "unauthorized"}']` and does not call `send_text`. A matching secret is not `404` and reaches the handler. |
| EW-06 | done | `tests/unit/api/test_send_campaign_worker.py` | Matching-secret test patches `api.handlers.worker_handler.client.send_text`, posts `phone` and `message`, and asserts both arguments, `200 OK`, and `[b'{"status":"sent"}']`. No live Twilio and no Datastore. |
| EW-07 | done | `docs/DEPLOYMENT.md`, `docs/operations/PRODUCTION.md`, `README.md`, `AGENTS.md`, `docs/ROADMAP.md` | Campaign worker is listed as present. `DEPLOYMENT.md` drops "not yet implemented". `PRODUCTION.md` adds the route. `README.md` adds the HTTP row and the Gaps bullet now says only Scheduler-from-CD is not done. `AGENTS.md` lists `POST /workers/send-campaign`. `ROADMAP.md` checks only `/workers/send-campaign`. Scheduler stays `[ ]`. `docs/MVP_SCOPE.md` was not edited. |
| EW-08 | done | `docs/ROADMAP-TASKS.md`, `docs/COMMERCIAL-LAUNCH.md`, `docs/specs/sdd/T030-send-campaign-worker-sdd.md`, `docs/specs/sdd/INDEX.md` | Checked T030 and commercial-launch item 26. Set this SDD status and the INDEX T030 row to `implemented` after EW-01–EW-07 and EW-09 held. |
| EW-09 | done | (no product files added) | Diff does not add Scheduler or CD wiring, `enqueue("send_campaign", ...)`, webhook queueing, entitlement or cadence or education-job changes, or a second Twilio client. `core/queues.py` was not changed. `send_campaign.worker_path` remains `/workers/send-campaign`. |

## Files touched

- `AGENTS.md`
- `CONTEXT.md`
- `PLAN.md`
- `README.md`
- `SPEC.md`
- `api/handlers/worker_handler.py`
- `api/routes.py`
- `docs/COMMERCIAL-LAUNCH.md`
- `docs/DEPLOYMENT.md`
- `docs/ROADMAP-TASKS.md`
- `docs/ROADMAP.md`
- `docs/operations/PRODUCTION.md`
- `docs/specs/sdd/INDEX.md`
- `docs/specs/sdd/T030-builder-report.md`
- `docs/specs/sdd/T030-send-campaign-worker-sdd.md`
- `tests/unit/api/test_internal_job_auth.py`
- `tests/unit/api/test_send_campaign_worker.py`

`CONTEXT.md`, `PLAN.md`, and `SPEC.md` are the handoff inputs carried onto this branch. They do not add worker behavior.

## Verification

- `uv run pytest tests/unit/api/test_internal_job_auth.py tests/unit/api/test_send_campaign_worker.py -q` — 12 passed
- `uv run ruff check api/handlers/worker_handler.py api/routes.py tests/unit/api/test_internal_job_auth.py tests/unit/api/test_send_campaign_worker.py` — all checks passed
- `uv run python quality/check_import_style.py` — import style OK
