# CONTEXT — WineAI (wineia)

> Read first. Product milestones: [`docs/ROADMAP.md`](docs/ROADMAP.md). Commercial launch checklist: [`docs/COMMERCIAL-LAUNCH.md`](docs/COMMERCIAL-LAUNCH.md). Micro-tasks: [`docs/ROADMAP-TASKS.md`](docs/ROADMAP-TASKS.md).

## Primary objective (current)

**T032** — Full async webhook replies via queue. WhatsApp inbound keeps **Claude generation synchronous** in the webhook request. Only the **Twilio outbound** (IA reply and limit-reached warning) is enqueued on Cloud Tasks `send_message` → `POST /workers/send-message`. The webhook returns `200` after enqueue is accepted.

The comparison contract is [`docs/specs/sdd/T032-async-webhook-replies-sdd.md`](docs/specs/sdd/T032-async-webhook-replies-sdd.md). Its **Expected work** list (EW-01…) is what the reviewer checks against the builder report. Do not add behavior that list does not name. On conflict, the SDD Expected work table wins over PLAN.md / SPEC.md.

Skip **T004** (GitHub admin).

## Decisions already made (parent defaults, 2026-11-15)

| Topic | Decision |
|-------|----------|
| Sync vs async boundary | Claude `generate_response` stays **in the webhook request**. Only Twilio outbound is async. |
| Limit-reached warning | Enqueued via the same path as IA replies. No sync `messaging_gateway.send_text` from `messaging_service` for product replies. |
| Cancel path | Datastore status update only; no outbound text. |
| Enqueue reuse | Reuse existing `enqueue_send_message` (or a shared helper if cleaner). Worker already exists — do not reinvent send-campaign. |
| Idempotency keys | Out of scope (optional later). |
| No regression | Twilio signature validation, IP/phone rate limits (T012), on-demand entitlements (T024) unchanged in behavior. |
| Ops docs | Document Twilio retry behavior when webhook returns 200 before the worker send completes. |
| Clean Architecture | Domain must not import infrastructure. Inject a `message_sender` / enqueue callable from the handler (same DI style as today's `messaging_gateway`). |
| Entitlement counter | Increment when a successful IA reply is **accepted for enqueue** (same moment relative to `generate_response` as today), not when the worker delivers. |
| `/ia/suggestions` | Out of scope (uses its own Twilio send path, not `messaging_service`). |

## Decisions made by the orchestrator

| Topic | Decision |
|-------|----------|
| Domain API | `process_incoming_message` takes `message_sender` (callable `(phone, message) -> None`) instead of `messaging_gateway`. Domain never calls Twilio or Cloud Tasks directly. |
| Handler wiring | `whatsapp_handler` injects `enqueue_send_message` from `domain.services.recommendation_service` as `message_sender` (reuse; that helper already owns Cloud Tasks). Do not construct a second Twilio client in the webhook for product replies. |
| Handler deps | Drop `messaging_gateway` from webhook `_create_dependencies` once unused by `process_incoming_message`. Keep repository + `ia_service`. |
| Order of operations (IA path) | `generate_response` → `message_sender(...)` → increment `messages_sent_today` / stamp `last_message_at` → `repository.update`. If enqueue raises, counter must not increment. |
| Limit path | On `not can_send_message`, call `message_sender` with the existing Portuguese warning string; return `{"status": "limit_reached"}`; do not call IA; do not increment. |
| Cancel path | Unchanged: set `status=canceled`, update repo, return; no `message_sender` call. |
| Worker / queues | No change to `worker_handler`, `core/queues.py`, or campaign worker. |
| Tests | Update domain messaging tests to assert `message_sender` calls instead of gateway `send_text`. Add/adjust webhook handler tests for the new kwarg. Coverage domain/core ≥ 95%. |

## Out of scope

- Idempotency keys on Cloud Tasks.
- Making Claude generation async / a second queue for IA.
- Changing `/ia/suggestions` Twilio send path.
- Changing worker payloads, campaign worker, Scheduler CD (T031), job auth, entitlement caps, webhook rate-limit algorithms.
- New pip dependencies; `docs/MVP_SCOPE.md`.
- T004 GitHub branch protection.

## Relevant files

| File | Role |
|------|------|
| `domain/services/messaging_service.py` | Replace sync gateway sends with injected `message_sender` |
| `api/handlers/whatsapp_handler.py` | Wire enqueue as `message_sender`; keep signature + phone rate limit |
| `domain/services/recommendation_service.py` | Existing `enqueue_send_message` to reuse |
| `api/handlers/worker_handler.py` | Existing `POST /workers/send-message` — do not reinvent |
| `infrastructure/queue/cloud_tasks_client.py`, `core/queues.py` | Existing queue wiring — unchanged unless a justified helper extract |
| `tests/unit/domain/test_messaging_service.py` | Domain contract tests |
| `tests/unit/api/test_whatsapp_webhook.py` | Handler wiring / signature regression |
| `docs/operations/PRODUCTION.md`, `docs/DEPLOYMENT.md`, `README.md` | Ops + gap line for async webhook / Twilio retries |
| `docs/decision.md` | Note webhook outbound is async after T032 |
| `docs/ROADMAP.md`, `docs/ROADMAP-TASKS.md`, `docs/COMMERCIAL-LAUNCH.md` (#15), `docs/specs/sdd/INDEX.md` | Status flips after EW hold |

## Acceptance criteria

See EW-01… in the SDD. In short:

- [ ] Product replies (IA + limit warning) leave the webhook only via enqueue → worker; no sync Twilio from messaging_service.
- [ ] Claude stays sync in the webhook; cancel stays Datastore-only.
- [ ] Counter increments only after enqueue acceptance for a processed IA reply.
- [ ] Signature validation, rate limits, entitlements behavior preserved.
- [ ] Ops docs cover Twilio 200-before-send / retry behavior; gap lines updated.
- [ ] Builder report + reviewer judge accept; pytest, ruff, import style; domain/core coverage ≥ 95%.

## Git policy (fixed)

Branch: `feat/t032-async-webhook-replies` from `origin/main` (no `cursor/` prefix — see [`docs/GIT_WORKFLOW.md`](docs/GIT_WORKFLOW.md)). **Never push to `main`.** Conventional Commits, English, lowercase subject. Parent creates the GitHub PR; leave PR URL unset if ManagePullRequest is parent-owned. Commit bodies wrap at 72 characters (commitlint `body-max-line-length` is 100).

## Agent handoff

On-call: [`.cursor/agents/on-call.md`](.cursor/agents/on-call.md).

Builder report path: `docs/specs/sdd/T032-builder-report.md` (one row per Expected work ID, files, done or skipped, plus Files touched). The reviewer reads that file, the SDD, and the diff, and is the judge. The reviewer does not edit any file.
