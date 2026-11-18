# SDD — Inbound WhatsApp image + audio (T074)

**Status:** draft  
**Task:** [T074](../../ROADMAP-TASKS.md)  
**Commercial-launch:** Phase 3 item #16a (planned)

## Problem

`POST /webhook/whatsapp` only reads Twilio form field `Body` (`extract_message`). There is no handling of `NumMedia`, `MediaUrlN`, or `MediaContentTypeN`.

Today:

- Image-only or audio-only inbound messages (empty `Body`) are accepted with HTTP 200 and **silently ignored** (`if phone and message` skips domain processing).
- Claude path is text-only; no STT for voice notes and no vision for bottle/label photos.
- Product promise (sommelier on WhatsApp) cannot answer “what wine is this?” from a photo or a spoken question.

## Goals

1. Detect inbound media on the Twilio WhatsApp webhook (at least **image** and **audio**).
2. Fetch media securely from Twilio media URLs (auth as required by Twilio docs — to be filled after product owner research).
3. Turn media into something the existing on-demand IA path can use:
   - **Audio** → transcription (STT) → text into `process_incoming_message` / `ia_service.generate_response`.
   - **Image** → multimodal Claude (or equivalent) with optional caption from `Body`.
4. Keep Clean Architecture: parser/handler HTTP concerns; domain orchestration; infrastructure for Twilio media fetch + STT/vision clients.
5. Respect existing gates: Twilio signature, webhook rate limits, on-demand entitlements, Claude daily budget, async outbound enqueue (T032).
6. Fail closed with a short Portuguese customer reply when media cannot be processed (unsupported type, download failure, STT/vision failure) — do not leave a silent 200 with no product response when the customer clearly sent media.

## Non-goals (this draft)

- Outbound sending of images/audio from WineAI (inbound only).
- Video, documents, stickers, location, contacts (may be deferred; document unsupported behavior).
- Persisting raw media blobs long-term in Datastore (prefer ephemeral processing; LGPD note in Expected work when expanded).
- Changing ENTRY/SUPERIOR quota semantics beyond counting a successful media turn as one on-demand IA turn (confirm in Expected work).

## Current code anchors

| Area | File |
|------|------|
| Webhook handler | `api/handlers/whatsapp_handler.py` |
| Body-only extract | `core/utils/twilio_webhook_parser.py` (`extract_message`) |
| Domain path | `domain/services/messaging_service.py` (`process_incoming_message`) |
| Claude text | `infrastructure/external/claude_client.py` / `domain/services/ia_service.py` |

## Docs to attach (owner research)

Fill links after reviewing Twilio + Meta WhatsApp media docs:

- [ ] Twilio inbound media fields (`NumMedia`, `MediaUrl{N}`, `MediaContentType{N}`)
- [ ] Twilio media download authentication
- [ ] Supported WhatsApp media types / size limits for the Twilio WhatsApp channel
- [ ] Claude multimodal image input constraints (size, MIME)
- [ ] STT option (provider TBD — ADR if new dependency)

## Acceptance criteria (draft)

- [ ] Image and audio inbound messages from known active customers produce a product reply (or explicit Portuguese unavailable/error copy), not a silent ignore.
- [ ] Text-only path unchanged.
- [ ] Unsupported media types get a clear Portuguese reply.
- [ ] Entitlements and Claude budget still apply.
- [ ] Unit tests cover parser media extraction and “media without Body” routing.
- [ ] PRODUCTION.md / WHATSAPP-COMPLIANCE.md note inbound media behavior.
- [ ] Full **Expected work (EW-xx)** table written before implementation (expand this SDD from draft → ready).

## Expected work

| ID | Work | Primary files |
|----|------|----------------|
| EW-00 | Expand this SDD with normative EW-01… after Twilio/media docs are attached; choose STT provider and multimodal shape (ADR if new dep). | `docs/specs/sdd/T074-inbound-whatsapp-media-sdd.md`, optional ADR |

*(Implementation EW rows intentionally deferred until docs research lands.)*

## Related

- [ROADMAP-TASKS.md](../../ROADMAP-TASKS.md) T074
- [ROADMAP.md](../../ROADMAP.md) M2
- [COMMERCIAL-LAUNCH.md](../../COMMERCIAL-LAUNCH.md) Phase 3
- [T032-async-webhook-replies-sdd.md](./T032-async-webhook-replies-sdd.md)
- [operations/WHATSAPP-COMPLIANCE.md](../../operations/WHATSAPP-COMPLIANCE.md)
- [operations/DATA-RETENTION.md](../../operations/DATA-RETENTION.md) (media ephemerality / LGPD)

## Revision history

| Date | Change |
|------|--------|
| 2026-11-18 | Initial draft — roadmap placeholder; owner to attach Twilio media docs before EW expansion |
