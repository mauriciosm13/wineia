# PLAN — T032 Async webhook replies via queue

Source of truth: `CONTEXT.md` and Expected work EW-01–EW-10 in `docs/specs/sdd/T032-async-webhook-replies-sdd.md`. On conflict, the SDD Expected work table wins.

Branch: `cursor/t032-async-webhook-replies-afd2` from `origin/main`.

`PLAN.md` is this handoff. It is not an Expected work product.

## Order

| # | Task | EW | Depends on |
|---|------|----|------------|
| 1 | Domain: inject `message_sender`, remove sync gateway | EW-01 | — |
| 2 | Cancel / limit / processed paths + failure test | EW-02–EW-05 | 1 |
| 3 | WhatsApp handler wiring + signature tests | EW-06, EW-07 | 1 |
| 4 | Ops / README / ROADMAP / decision docs | EW-08 | 3 |
| 5 | Diff and coverage gate | EW-10 | 1–4 |
| 6 | Status flips | EW-09 | 5 |
| 7 | Builder report | EW-01–EW-10 | 6 |

## Tasks

### 1. Domain message_sender (EW-01)

Files: `domain/services/messaging_service.py`.

- Replace parameter `messaging_gateway` with `message_sender`.
- Call `message_sender(phone, text)` instead of `messaging_gateway.send_text(...)`.
- Do not import infrastructure.

### 2. Path behavior and tests (EW-02–EW-05)

Files: `tests/unit/domain/test_messaging_service.py` (+ messaging_service).

- Cancel: no sender call.
- Limit: sender gets warning; no IA; no increment.
- Processed: generate → sender → increment; assert sender args.
- Sender raises: counter unchanged; no successful increment update.

### 3. Handler wiring (EW-06, EW-07)

Files: `api/handlers/whatsapp_handler.py`, `tests/unit/api/test_whatsapp_webhook.py`.

- Import and pass `enqueue_send_message` as `message_sender`.
- Remove Twilio gateway from webhook deps if unused.
- Keep signature 403 / 200 contracts; entitlement tests stay green.

### 4. Docs (EW-08)

- PRODUCTION.md / DEPLOYMENT.md: enqueue path + Twilio 200-before-send.
- README Gaps: remove sync-inbound claim.
- ROADMAP M2 async checkbox.
- decision.md: close sync-webhook Twilio gap wording.

### 5–7. Gate, status, report

- pytest, ruff, import style; domain/core coverage ≥ 95%.
- Flip T032 / CL #15 / SDD + INDEX to implemented only when EW hold.
- Write `docs/specs/sdd/T032-builder-report.md`.

## Out of scope (do not do)

Idempotency keys; async Claude; `/ia/suggestions`; worker/queue/Scheduler changes; entitlement number changes; T004.
