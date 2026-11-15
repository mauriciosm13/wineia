# T032 builder report

Branch: `cursor/t032-async-webhook-replies-afd2` (from `origin/main`).

| ID | Result (`done` or `skipped`) | Files | What changed |
|----|-------------------------------|-------|----------------|
| EW-01 | done | `domain/services/messaging_service.py` | Replaced `messaging_gateway` with `message_sender` callable `(phone, message)`. No infrastructure import; no Twilio call in domain. |
| EW-02 | done | `domain/services/messaging_service.py`, `tests/unit/domain/test_messaging_service.py` | Cancel sets Datastore `canceled` only; sender and IA not called (`test_cancelar_sets_canceled_status`). |
| EW-03 | done | same | Limit path calls `message_sender` with the Portuguese warning; returns `limit_reached`; no IA; counter unchanged (`test_limit_reached_at_two_messages`, `test_inactive_customer_cannot_send`). |
| EW-04 | done | same | Processed path: `generate_response` → `message_sender(phone, response)` → increment (`test_processed_increments_counter`). |
| EW-05 | done | same | Sender raise leaves `messages_sent_today` at 0 and does not stamp `last_message_at` (`test_processed_sender_failure_does_not_increment`). |
| EW-06 | done | `api/handlers/whatsapp_handler.py`, `tests/unit/api/test_whatsapp_webhook.py` | Wires `message_sender=enqueue_send_message`; deps drop Twilio gateway; 403 invalid signature; 200 received; deps identity test. |
| EW-07 | done | `tests/unit/api/test_whatsapp_webhook.py`, `tests/unit/api/test_webhook_rate_limit.py`, messaging entitlement tests | Signature, phone rate-limit, and tier entitlement tests remain green; mock deps updated to `message_sender`. |
| EW-08 | done | `docs/operations/PRODUCTION.md`, `docs/DEPLOYMENT.md`, `README.md`, `docs/ROADMAP.md`, `docs/decision.md` | Documented enqueue + Twilio 200-before-send; README gap removed; M2 async checked; decision.md no longer lists sync Twilio outbound as open. |
| EW-09 | done | `docs/ROADMAP-TASKS.md`, `docs/COMMERCIAL-LAUNCH.md`, `docs/specs/sdd/T032-async-webhook-replies-sdd.md`, `docs/specs/sdd/INDEX.md` | Checked T032 and CL #15; SDD + INDEX status `implemented` after EW-01–EW-08 and EW-10 held. |
| EW-10 | done | (no product files out of scope) | Diff does not change worker/campaign contracts, `core/queues.py`, Scheduler CD, `/ia/suggestions`, idempotency keys, or entitlement limit numbers. Coverage ≥ 95%; pytest/ruff/import style pass. |

## Files touched

- `CONTEXT.md`
- `PLAN.md`
- `SPEC.md`
- `README.md`
- `api/handlers/whatsapp_handler.py`
- `domain/services/messaging_service.py`
- `docs/COMMERCIAL-LAUNCH.md`
- `docs/DEPLOYMENT.md`
- `docs/ROADMAP-TASKS.md`
- `docs/ROADMAP.md`
- `docs/decision.md`
- `docs/operations/PRODUCTION.md`
- `docs/specs/sdd/INDEX.md`
- `docs/specs/sdd/T032-async-webhook-replies-sdd.md`
- `docs/specs/sdd/T032-builder-report.md`
- `tests/unit/api/test_webhook_rate_limit.py`
- `tests/unit/api/test_whatsapp_webhook.py`
- `tests/unit/domain/test_messaging_service.py`

`CONTEXT.md`, `PLAN.md`, and `SPEC.md` are handoff inputs. They do not add runtime behavior beyond documenting the contract.

## Verification

- `PYTHONPATH=. python3 -m pytest --cov=domain --cov=core --cov-report=term-missing -q` — 189 passed; Total coverage 95.48% (fail_under 95)
- `python3 -m ruff check api/handlers/whatsapp_handler.py domain/services/messaging_service.py tests/unit/domain/test_messaging_service.py tests/unit/api/test_whatsapp_webhook.py tests/unit/api/test_webhook_rate_limit.py` — All checks passed
- `python3 quality/check_import_style.py` — Import style OK
