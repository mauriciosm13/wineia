# SPEC — T032 Async webhook replies via queue

**Status:** ready for implementation  
**Task:** T032 ([docs/ROADMAP-TASKS.md](docs/ROADMAP-TASKS.md))  
**Branch:** `cursor/t032-async-webhook-replies-afd2`  
**Binding sources:** [CONTEXT.md](CONTEXT.md), [PLAN.md](PLAN.md), [docs/specs/sdd/T032-async-webhook-replies-sdd.md](docs/specs/sdd/T032-async-webhook-replies-sdd.md) (Expected work EW-01–EW-10).

This file is the implementation contract. If it ever disagrees with the SDD Expected work table, the SDD wins.

## Problem

Inbound WhatsApp replies call Twilio synchronously inside the webhook after Claude generation. Limit warnings do the same. Scheduled sends already enqueue; webhook product replies do not.

## Goals

- Product outbound text (IA reply + limit warning) enqueued via `send_message` → `/workers/send-message`.
- Claude stays in the webhook request.
- Domain uses an injected `message_sender`; no infrastructure import from messaging_service.
- Counter increments on enqueue accept for processed IA replies.
- Document Twilio 200-before-worker-send behavior.

## Scope

| Slice | EW | Files |
|-------|----|-------|
| Domain `message_sender` | EW-01 | `domain/services/messaging_service.py` |
| Cancel / limit / processed / raise | EW-02–EW-05 | messaging_service + `tests/unit/domain/test_messaging_service.py` |
| Handler wiring + regressions | EW-06–EW-07 | `api/handlers/whatsapp_handler.py`, webhook tests |
| Ops / README / ROADMAP / decision | EW-08 | PRODUCTION.md, DEPLOYMENT.md, README.md, ROADMAP.md, decision.md |
| Status flips | EW-09 | ROADMAP-TASKS, COMMERCIAL-LAUNCH #15, SDD, INDEX |
| Diff gate | EW-10 | whole diff |
| Builder report | EW-01–EW-10 | `docs/specs/sdd/T032-builder-report.md` |

## Out of scope

- Idempotency keys; async Claude; `/ia/suggestions` send path.
- Worker/campaign/queue path changes; Scheduler CD; job auth.
- Entitlement limit number changes; webhook rate-limit algorithm changes.
- New pip deps; `docs/MVP_SCOPE.md`; T004.

## Expected behavior (summary)

1. Webhook: signature + phone limit unchanged → `process_incoming_message(..., message_sender=enqueue_send_message, ...)`.
2. Cancel: Datastore only.
3. Limit: enqueue warning; no IA; no increment.
4. Processed: sync Claude → enqueue response → increment → update.
5. Webhook HTTP 200 after process returns; Twilio does not HTTP-retry 200s; worker owns delivery.

## Acceptance

All EW-01–EW-10 true; builder report written; reviewer judge accepts; pytest + ruff + import style; domain/core coverage ≥ 95%.
