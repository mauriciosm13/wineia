# SDD — Twilio inbound media parser (T075)

**Status:** implemented  

**Task:** [T075](../../ROADMAP-TASKS.md) · parent [T074](./T074-inbound-whatsapp-media-sdd.md)  
**Comparison contract:** this Expected work list is what the reviewer checks against [T075-builder-report.md](./T075-builder-report.md).

## Problem

Webhook only uses `Body`. Media-only messages never enter `process_incoming_message`.

## Goals

- Extract `NumMedia`, `MediaUrl0`, `MediaContentType0` (WhatsApp: at most one attachment).
- When `NumMedia >= 1`, still invoke domain even if `Body` is empty.
- Keep signature + rate limits unchanged; text-only path unchanged when `NumMedia=0`.
- Fail closed for media-only until T076+ can process: Portuguese customer reply (no silent ignore).

## Non-goals

- Authenticated media download (T076).
- STT / vision (T077 / T078).
- Ops docs beyond marking T075 progress (T079 owns PRODUCTION / compliance notes).
- Outbound media; payments T040–T043.

## Behavior

### Parser

`extract_inbound_media(payload)` returns a dict when `NumMedia >= 1`:

| Key | Source | Notes |
|-----|--------|--------|
| `num_media` | `NumMedia` | int; WhatsApp ≤ 1 |
| `url` | `MediaUrl0` | may be None if Twilio omits |
| `content_type` | `MediaContentType0` | MIME string; may be None |

Returns `None` when `NumMedia` is missing, unparsable, or `< 1`.

`has_inbound_media(media)` is true when media is a non-empty dict with `num_media >= 1`.

### Handler

After signature + phone extract + rate limit (unchanged):

- Invoke `process_incoming_message` when `phone` and (`Body` text **or** inbound media).
- Pass `inbound_media=` from the parser (or omit/`None` when absent).
- Text-only (`NumMedia=0` / no media) behavior unchanged.

### Domain

`process_incoming_message(..., inbound_media=None)`:

1. Unknown customer / cancel / entitlement / budget gates unchanged for text.
2. When there is **no** non-empty text body and `has_inbound_media(inbound_media)`:
   - Do **not** call IA with an empty string.
   - Call `message_sender(phone, MEDIA_UNAVAILABLE_MESSAGE)` with a fixed Portuguese string stating media cannot be processed yet.
   - Do **not** increment `messages_sent_today` (not a successful IA turn).
   - Return `{"status": "media_unprocessable"}`.
3. When there is non-empty text (with or without media): existing text IA path; media metadata may be accepted but is unused until T076+.

## Acceptance criteria

- Unit tests: media-only payload is not silently dropped; text-only still works.
- Handler/parser APIs documented for T076+.
- Domain/core coverage ≥ 95%; ruff + import style pass.

## Expected work

The builder implements only these items. The reviewer marks each **match**, **gap**, or **extra**.

| ID | Must be true when the work is done | Where |
|----|-------------------------------------|--------|
| EW-01 | `extract_inbound_media(payload)` returns `{num_media, url, content_type}` when `NumMedia >= 1`, else `None`. Parses `NumMedia` as int; reads `MediaUrl0` / `MediaContentType0`. | `core/utils/twilio_webhook_parser.py` |
| EW-02 | `has_inbound_media(media)` is true iff media is present with `num_media >= 1`. | same |
| EW-03 | `whatsapp_handler` invokes domain when `phone` and (non-empty `Body` **or** inbound media). Signature 403 and phone rate-limit 429 paths unchanged. Text-only (`NumMedia=0`) still calls domain with message only. | `api/handlers/whatsapp_handler.py` |
| EW-04 | `process_incoming_message` accepts optional `inbound_media`. Media-only (empty/whitespace/`None` Body + media): sends `MEDIA_UNAVAILABLE_MESSAGE` via `message_sender`, does not call IA, does not increment counter, returns `media_unprocessable`. | `domain/services/messaging_service.py` |
| EW-05 | Non-empty text path (with or without media) still runs existing IA + counter behavior; cancelar still cancels without treating media specially. | messaging_service + domain tests |
| EW-06 | Unit tests cover: parser media extraction / no-media; handler media-only routes to domain; handler empty Body + NumMedia=0 does not call domain; domain media-only Portuguese reply without IA/increment; text-only regression. | `tests/unit/core/test_twilio_webhook_parser.py`, `tests/unit/api/test_whatsapp_webhook.py`, `tests/unit/domain/test_messaging_service.py` |
| EW-07 | Only after EW-01–EW-06 and EW-08 hold: `ROADMAP-TASKS.md` checks **T075**; this SDD status `implemented`; `INDEX.md` T075 row `implemented`. Do not check T076–T079 or payments. | those files |
| EW-08 | Diff does not implement T076 download, T077 STT, T078 vision, payments, or long-term blob storage. Domain must not import infrastructure. Domain/core coverage ≥ 95%. pytest, ruff, and `python quality/check_import_style.py` pass. | whole diff |

## Builder report

After implementation, write `docs/specs/sdd/T075-builder-report.md`:

| ID | Result (`done` or `skipped`) | Files | What changed |
|----|-------------------------------|-------|----------------|

Add a **Files touched** list and exact test commands with results. The reviewer treats any path not justified by an ID as **extra**.

## Reviewer comparison

Read this file, the builder report, and the diff. Return only:

- One line per ID: `EW-xx match|gap — evidence`
- Extras: paths or behavior not in the table
- Bugs that break an ID
- Verdict: accept or reject

Do not implement.

## Related

- [T074](./T074-inbound-whatsapp-media-sdd.md) research (webhook fields)
- `core/utils/twilio_webhook_parser.py`, `api/handlers/whatsapp_handler.py`
- [CONTEXT.md](../../../CONTEXT.md)

## Revision history

| Date | Change |
|------|--------|
| 2026-11-18 | Initial draft slice |
| 2026-11-18 | Expand Expected work EW-01–EW-08; media-only Portuguese fail-closed until T076+ |
| 2026-11-18 | Status `implemented` after EW-01–EW-08 hold |
