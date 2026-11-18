# SDD — Twilio inbound media parser (T075)

**Status:** draft  
**Task:** [T075](../../ROADMAP-TASKS.md) · parent [T074](./T074-inbound-whatsapp-media-sdd.md)

## Problem

Webhook only uses `Body`. Media-only messages never enter `process_incoming_message`.

## Goals

- Extract `NumMedia`, `MediaUrl0`, `MediaContentType0` (WhatsApp: at most one attachment).
- When `NumMedia >= 1`, still invoke domain even if `Body` is empty.
- Keep signature + rate limits unchanged; text-only path unchanged when `NumMedia=0`.

## Acceptance criteria

- Unit tests: media-only payload is not silently dropped; text-only still works.
- Handler/parser APIs documented for T076+.

## Related

- [T074](./T074-inbound-whatsapp-media-sdd.md) research (webhook fields)
- `core/utils/twilio_webhook_parser.py`, `api/handlers/whatsapp_handler.py`

## Revision history

| Date | Change |
|------|--------|
| 2026-11-18 | Initial draft slice |
