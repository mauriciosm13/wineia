# SDD — Full async webhook replies via queue (T032)

**Status:** implemented  
**Task:** [T032](../../ROADMAP-TASKS.md)  
**Comparison contract:** this Expected work list is what the reviewer checks against [T032-builder-report.md](./T032-builder-report.md).

## Problem

`POST /webhook/whatsapp` validates the Twilio signature, applies phone rate limits, then calls `process_incoming_message`, which generates Claude copy and calls `messaging_gateway.send_text` **inside the same request**. Limit-reached warnings use the same sync Twilio path. A slow Claude or Twilio call holds the webhook open. Scheduled jobs already enqueue via `enqueue_send_message` → Cloud Tasks `send_message` → `POST /workers/send-message`; inbound product replies do not.

## Goals

- Enqueue outbound product replies (IA answer and daily-limit warning) on Cloud Tasks `send_message`.
- Keep Claude generation synchronous in the webhook request.
- Return `200` from the webhook after enqueue is accepted (same HTTP success contract as today).
- Keep domain free of infrastructure imports: inject a `message_sender` callable from the handler.
- Document Twilio retry behavior when the webhook returns 200 before the worker finishes sending.

## Non-goals

- Idempotency keys on Cloud Tasks (optional later).
- Making Claude / IA generation asynchronous or adding a new queue for generation.
- Changing `/ia/suggestions` (it does not use `messaging_service`).
- Changing `worker_handler`, campaign worker, `core/queues.py` worker paths, Scheduler CD (T031), job auth, entitlement caps, or webhook IP/phone rate-limit algorithms.
- New pip dependencies. `docs/MVP_SCOPE.md`.
- T004 GitHub branch protection.

## Behavior

### Sync vs async boundaries

| Step | Where | Sync/async |
|------|--------|------------|
| IP rate limit | Router | Sync |
| Twilio signature + phone rate limit | `whatsapp_handler` | Sync |
| Customer load, cancel, entitlement gate, Claude `generate_response` | `process_incoming_message` / IA | Sync (in webhook request) |
| Outbound product text (IA reply or limit warning) | `message_sender` → Cloud Tasks → `POST /workers/send-message` → Twilio | **Async** (enqueue in webhook; send in worker) |
| Cancel (`cancelar`) | Datastore update only | Sync; **no** outbound text |
| Webhook HTTP response | Handler returns `200` `{"status":"received"}` after `process_incoming_message` returns | Sync; may complete before the worker delivers WhatsApp |

### Domain contract

`process_incoming_message(phone, message, repository, message_sender, ia_service, now=None)`:

1. Unknown customer → `None`; no sender call.
2. Cancel → set `status=canceled`, `repository.update`, return `{"status":"canceled"}`; no sender call; no IA.
3. Reset daily counter if needed; if `not can_send_message` → `message_sender(phone, warning)` with the existing Portuguese limit text; return `{"status":"limit_reached"}`; no IA; no counter increment.
4. Else → `response = ia_service.generate_response(...)` → `message_sender(phone, response)` → increment `messages_sent_today`, stamp `last_message_at`, `repository.update` → return `{"status":"processed", "message": response}`.

**Entitlement timing:** the on-demand counter increments when the IA reply has been **accepted for enqueue** (immediately after a successful `message_sender` call), not when the worker delivers. If `message_sender` raises, the counter must not increment.

### Handler wiring

`whatsapp_handler` injects `enqueue_send_message` (from `domain.services.recommendation_service`) as `message_sender`. It does not call Twilio sync for product replies. Signature validation and phone rate limits stay as today.

### Twilio retries (ops)

Twilio retries inbound webhooks on non-2xx or timeout. After this change the webhook can return **200 before** the worker has sent WhatsApp. A 200 means Twilio will **not** retry that delivery attempt for HTTP failure; delivery failures after enqueue are the worker / Cloud Tasks concern. Operators must not expect a second webhook retry to “finish” a send that was already enqueued. Document this in PRODUCTION.md / DEPLOYMENT.md.

## Expected work

The builder implements only these items. The reviewer marks each **match**, **gap**, or **extra**.

| ID | Must be true when the work is done | Where |
|----|-------------------------------------|--------|
| EW-01 | `process_incoming_message` accepts `message_sender` (callable `(phone, message) -> None`) instead of `messaging_gateway`. Domain module does not import `infrastructure` and does not call Twilio. | `domain/services/messaging_service.py` |
| EW-02 | Cancel path: Datastore status `canceled` only; `message_sender` is not called; IA is not called. | messaging_service + domain tests |
| EW-03 | Limit-reached path: calls `message_sender(phone, warning)` with the existing Portuguese warning; returns `limit_reached`; does not call IA; does not increment `messages_sent_today`. | same |
| EW-04 | Processed path: `generate_response` then `message_sender(phone, response)` then increment counter and update customer. Tests prove the sender is called with the IA text and the counter becomes `prior + 1` only after a successful sender call. | same |
| EW-05 | If `message_sender` raises on the processed path, `messages_sent_today` is not incremented and `repository.update` is not called for that increment (counter stays at the pre-call value). | domain tests |
| EW-06 | `whatsapp_handler` wires `message_sender=enqueue_send_message` (reuse existing helper). `_create_dependencies` no longer supplies a Twilio `messaging_gateway` for the webhook product path. Signature rejection still 403 before process; valid signature still 200 `{"status":"received"}`. | `api/handlers/whatsapp_handler.py`, `tests/unit/api/test_whatsapp_webhook.py` |
| EW-07 | No regression: Twilio signature validation, IP/phone rate-limit modules, and on-demand entitlement helpers (`can_send_on_demand` / tier caps) keep their existing behavior; this diff does not weaken them. | webhook tests + messaging entitlement tests |
| EW-08 | Docs: PRODUCTION.md and/or DEPLOYMENT.md state that product WhatsApp replies are enqueued and that a webhook 200 can precede worker delivery (Twilio will not HTTP-retry a 200). README Gaps no longer claims inbound replies are synchronous. ROADMAP M2 “Async queue for replies” is checked. `docs/decision.md` no longer lists sync webhook Twilio outbound as an open gap. | those docs |
| EW-09 | Only after EW-01–EW-08 and EW-10 hold: `ROADMAP-TASKS.md` checks T032, `COMMERCIAL-LAUNCH.md` checks item 15, this SDD status is `implemented`, and `INDEX.md` matches. | those files |
| EW-10 | Diff does not change worker/campaign contracts, `core/queues.py` worker paths, Scheduler CD, `/ia/suggestions` send path, idempotency keys, or entitlement limit numbers. Domain/core coverage stays ≥ 95%. pytest, ruff, and `python quality/check_import_style.py` pass. | whole diff |

## Builder report

After implementation, write `docs/specs/sdd/T032-builder-report.md`:

| ID | Result (`done` or `skipped`) | Files | What changed |
|----|-------------------------------|-------|----------------|

Add a **Files touched** list of every path in the diff and the exact test commands with results. The reviewer treats any path not justified by an ID as **extra**.

## Reviewer comparison

Read this file, the builder report, and the diff. Return only:

- One line per ID: `EW-xx match|gap — evidence`
- Extras: paths or behavior not in the table
- Bugs that break an ID or leave sync Twilio product sends in `messaging_service`
- Verdict: accept or reject

Do not implement.

## Related

- [CONTEXT.md](../../../CONTEXT.md)
- [T030-send-campaign-worker-sdd.md](./T030-send-campaign-worker-sdd.md)
- [on-demand-entitlements-sdd.md](../on-demand-entitlements-sdd.md)
- [webhook-rate-limit.md](../webhook-rate-limit.md)
- [DEPLOYMENT.md](../../DEPLOYMENT.md)
- [PRODUCTION.md](../../operations/PRODUCTION.md)
- [decision.md](../../decision.md)

## Revision history

| Date | Change |
|------|--------|
| 2026-11-10 | Initial stub |
| 2026-11-15 | Orchestrator checklist EW-01–EW-10: sync IA, async Twilio via enqueue, inject message_sender, counter on enqueue accept, Twilio 200-before-send docs |
