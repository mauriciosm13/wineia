# CONTEXT — WineAI (wineia)

> Read first. Product milestones: [`docs/ROADMAP.md`](docs/ROADMAP.md). Commercial launch checklist: [`docs/COMMERCIAL-LAUNCH.md`](docs/COMMERCIAL-LAUNCH.md). Micro-tasks: [`docs/ROADMAP-TASKS.md`](docs/ROADMAP-TASKS.md).

## Primary objective (current)

**T030** — Implement `POST /workers/send-campaign` so the `wine-campaigns` queue has a worker that matches the existing `POST /workers/send-message` contract.

The comparison contract is [`docs/specs/sdd/T030-send-campaign-worker-sdd.md`](docs/specs/sdd/T030-send-campaign-worker-sdd.md). Its **Expected work** list is what the reviewer checks against the builder’s change list. Do not add behavior that list does not name.

## Requirements

- Register `POST /workers/send-campaign` in `api/routes.py`.
- Handler accepts the same JSON body as `handle_send_message`: `phone` and `message`.
- Handler sends via the existing module-level Twilio client (`client.send_text`) and returns `200` with `{"status":"sent"}`.
- Internal job auth already applies to every `/workers/` path. Do not add a second auth scheme. Add a test that `/workers/send-campaign` is covered.
- Keep `core/queues.py` `send_campaign.worker_path` as `/workers/send-campaign`. Do not provision queues or Scheduler (that is T031).
- Share one parse-and-send function between the two worker handlers so the payload contract cannot drift.
- Update operator docs that still say the campaign worker is missing.
- Unit tests with a fake or patched `send_text`. No Datastore and no live Twilio.

## Out of scope

- T004 GitHub branch protection.
- T031 Cloud Scheduler in CD.
- T032 async webhook replies.
- T060 / T061 IA caps and global budget.
- Enqueueing a new campaign job. Nothing in the repo calls `enqueue("send_campaign", ...)` today; do not invent a producer.
- Changing on-demand entitlements, recommendation cadence, or education jobs.
- Editing `docs/MVP_SCOPE.md`.
- New status codes that `handle_send_message` does not already return. Missing keys and bad JSON stay as they are on the message worker (uncaught).

## Decisions already made

| Topic | Decision |
|-------|----------|
| Next task | T030. T004 is GitHub admin, not this activity. T060 stays later. |
| Contract | Mirror `handle_send_message`. Same keys, same Twilio call, same `200` body. |
| Auth | Prefix rule in `api/internal_job_auth.py` already covers `/workers/send-campaign`. |
| Client | Reuse `api/handlers/worker_handler.py` module-level `client`. Do not construct a second Twilio client. |
| Queue | `wine-campaigns` / `worker_path` already set. No queue-config change required unless a test is missing. |
| Branch | Implement on `feat/t030-send-campaign-worker` cut from `main`. Do not commit T030 onto `feature/recon-planner`. Do not push. |
| Review | Builder writes a change list keyed by Expected work IDs. Reviewer compares that list to the SDD and reports match, gap, or extra. |

## Relevant files

| File | Role |
|------|------|
| `api/handlers/worker_handler.py` | `handle_send_message`; add shared send + `handle_send_campaign` |
| `api/routes.py` | Route table |
| `api/internal_job_auth.py` | `/jobs/` and `/workers/` secret check |
| `core/queues.py` | `send_campaign` → `/workers/send-campaign` |
| `infrastructure/queue/cloud_tasks_client.py` | Already posts to `worker_path` with `X-Job-Internal-Secret` |
| `docs/specs/sdd/T030-send-campaign-worker-sdd.md` | Expected-work checklist for the reviewer |
| `docs/DEPLOYMENT.md` | Still says the worker is not implemented |
| `docs/operations/PRODUCTION.md` | Route table; update in the same change |
| `tests/unit/api/test_internal_job_auth.py` | Auth path coverage |

## Acceptance criteria

- [ ] `EW-01` Shared outbound helper used by both worker handlers.
- [ ] `EW-02` `handle_send_campaign` reads `phone` and `message` and calls `client.send_text`.
- [ ] `EW-03` Success response is `200` and `{"status":"sent"}`.
- [ ] `EW-04` `ROUTES["/workers/send-campaign"]` is `handle_send_campaign`.
- [ ] `EW-05` Unauthorized `POST /workers/send-campaign` returns 401 before the handler. Authorized request reaches the handler.
- [ ] `EW-06` Unit test patches `send_text` and asserts phone, message, status, and body.
- [ ] `EW-07` `DEPLOYMENT.md`, `PRODUCTION.md`, `README.md`, and `AGENTS.md` list the route as present. `ROADMAP.md` marks only `/workers/send-campaign` done. Scheduler stays open.
- [ ] `EW-08` `ROADMAP-TASKS.md` T030 and `COMMERCIAL-LAUNCH.md` item 26 checked. SDD index status is `implemented` only after the code matches the checklist.
- [ ] `EW-09` No Scheduler, no webhook-queue change, no new campaign producer, no second Twilio client.
- [ ] pytest, ruff, and `python quality/check_import_style.py` pass for the touched tests. Domain/core coverage gate stays ≥ 95% if the gate runs.

## Git policy (fixed)

Branch: `feat/t030-send-campaign-worker` from `main`. See [`docs/GIT_WORKFLOW.md`](docs/GIT_WORKFLOW.md). **Never push to `main`.** Do not push unless the user asks.

## Agent handoff

On-call: [`.cursor/agents/on-call.md`](.cursor/agents/on-call.md).

Builder report path: `docs/specs/sdd/T030-builder-report.md` (one row per Expected work ID, files touched, done or skipped). Reviewer reads that file and the SDD. Reviewer does not edit either file.
