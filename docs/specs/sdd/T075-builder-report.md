# T075 builder report

Branch: `feat/t075-twilio-media-parser` (from `origin/main`).

| ID | Result (`done` or `skipped`) | Files | What changed |
|----|-------------------------------|-------|----------------|
| EW-01 | done | `core/utils/twilio_webhook_parser.py` | Added `extract_inbound_media`: parses `NumMedia` as int; returns `{num_media, url, content_type}` from `MediaUrl0` / `MediaContentType0` when `num_media >= 1`, else `None`. |
| EW-02 | done | same | Added `has_inbound_media(media)` true iff dict with `num_media >= 1`. |
| EW-03 | done | `api/handlers/whatsapp_handler.py`, `tests/unit/api/test_whatsapp_webhook.py` | Routes when phone + (non-empty Body or inbound media); passes `inbound_media`; signature 403 unchanged; text-only still works; empty Body + NumMedia=0 does not call domain. |
| EW-04 | done | `domain/services/messaging_service.py` | Optional `inbound_media`; media-only sends `MEDIA_UNAVAILABLE_MESSAGE`, no IA, no counter increment, returns `media_unprocessable`. |
| EW-05 | done | `domain/services/messaging_service.py`, `tests/unit/domain/test_messaging_service.py` | Text + media still uses IA path; cancelar with media still cancels without sender/IA. |
| EW-06 | done | parser / webhook / messaging unit tests | Covers media extraction, media-only routing, empty without media skip, media-only Portuguese reply, text-only regression. |
| EW-07 | done | `docs/ROADMAP-TASKS.md`, `docs/specs/sdd/INDEX.md`, `docs/specs/sdd/T075-twilio-media-parser-sdd.md` | T075 checked / `implemented` after EW-01–EW-06 and EW-08. |
| EW-08 | done | whole diff | No T076 download, STT, vision, payments, or blob storage. Domain imports core only (not infrastructure). Coverage ≥ 95%; pytest / ruff / import style pass. |

## Files touched

- `CONTEXT.md`
- `api/handlers/whatsapp_handler.py`
- `core/utils/twilio_webhook_parser.py`
- `domain/services/messaging_service.py`
- `docs/ROADMAP-TASKS.md`
- `docs/specs/sdd/INDEX.md`
- `docs/specs/sdd/T075-builder-report.md`
- `docs/specs/sdd/T075-twilio-media-parser-sdd.md`
- `tests/unit/api/test_whatsapp_webhook.py`
- `tests/unit/core/test_twilio_webhook_parser.py`
- `tests/unit/domain/test_messaging_service.py`

## Verification

- `PYTHONPATH=. python3 -m pytest --cov=domain --cov=core --cov-report=term-missing -q` — Total coverage 96.37% (≥95%)
- `python3 -m ruff check` on touched code/tests — All checks passed
- `python3 quality/check_import_style.py` — Import style OK
