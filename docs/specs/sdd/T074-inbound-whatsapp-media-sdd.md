# SDD — Inbound WhatsApp image + audio (T074)

**Status:** draft (Twilio media research attached; EW expansion + STT/vision ADR still open)  
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
2. Fetch media securely from Twilio `MediaUrl0` with HTTP Basic Auth (see research below).
3. Turn media into something the existing on-demand IA path can use:
   - **Audio** → transcription (STT) → text into `process_incoming_message` / `ia_service.generate_response`.
   - **Image** → multimodal Claude (or equivalent) with optional caption from `Body`.
4. Keep Clean Architecture: parser/handler HTTP concerns; domain orchestration; infrastructure for Twilio media fetch + STT/vision clients.
5. Respect existing gates: Twilio signature, webhook rate limits, on-demand entitlements, Claude daily budget, async outbound enqueue (T032).
6. Fail closed with a short Portuguese customer reply when media cannot be processed (unsupported type, download failure, STT/vision failure) — do not leave a silent 200 with no product response when the customer clearly sent media.

## Non-goals (this draft)

- Outbound sending of images/audio from WineAI (inbound only for T074).
- Video, documents, stickers, location, contacts (reply with unsupported copy).
- Persisting raw media blobs long-term in Datastore (prefer ephemeral processing; LGPD).
- Changing ENTRY/SUPERIOR quota semantics beyond counting a successful media turn as one on-demand IA turn (confirm in Expected work).

## Current code anchors

| Area | File |
|------|------|
| Webhook handler | `api/handlers/whatsapp_handler.py` |
| Body-only extract | `core/utils/twilio_webhook_parser.py` (`extract_message`) |
| Domain path | `domain/services/messaging_service.py` (`process_incoming_message`) |
| Claude text | `infrastructure/external/claude_client.py` / `domain/services/ia_service.py` |

## Research — Twilio WhatsApp media (2026-11-18)

The [WhatsApp quickstart](https://www.twilio.com/docs/whatsapp/quickstart) covers **text** send/receive only. Inbound media is documented in sibling Twilio pages (same webhook shape as SMS/MMS).

### Webhook fields (inbound)

Same `application/x-www-form-urlencoded` POST we already parse. Relevant parameters ([webhook request guide](https://www.twilio.com/docs/messaging/guides/webhook-request)):

| Parameter | Meaning |
|-----------|---------|
| `Body` | Text (may be empty when media-only) |
| `NumMedia` | Count of attachments (`"0"` or `"1"` for WhatsApp) |
| `MediaUrl0` | URL of the media file (WhatsApp: **one attachment per message** → always index `0`) |
| `MediaContentType0` | MIME type Twilio detected (e.g. `image/jpeg`) |

Tutorials: [Python media](https://www.twilio.com/docs/whatsapp/tutorial/send-and-receive-media-messages-whatsapp-python), [API overview — receiving](https://www.twilio.com/docs/whatsapp/api) (`Body` + `MediaUrl0`; images JPG/JPEG/PNG, audio, PDF; overview also cites **16MB** per message for inbound).

### Download auth

[`Media` resource](https://www.twilio.com/docs/messaging/api/media-resource): Twilio enforces **HTTP Basic Auth** on media URLs. Prefer **API key SID + secret**; Account SID + Auth Token also work. `GET MediaUrl0` typically **307-redirects** to a short-lived CDN URL (`mms.twiliocdn.com`, ~4h) — follow redirects and do not expose credentials to clients.

WineAI already has `TWILIO_ACCOUNT_SID` / `TWILIO_AUTH_TOKEN` for signature validation; media fetch reuses those (or API key if we add them later).

### Supported MIME types (channel)

From [Guidance on WhatsApp Media Messages](https://www.twilio.com/docs/whatsapp/guidance-whatsapp-media-messages):

| Kind | Formats |
|------|---------|
| Images | JPG, JPEG, PNG, WEBP\* (webp = stickers; extra rules) |
| Audio | OGG\*\*, AMR, 3GP, AAC, MPEG |
| Documents | PDF, DOC, DOCX, PPTX, XLSX |
| Video | MP4 (H.264 + AAC) |
| Contacts | vCard (`.vcf`) |

\* sticker constraints · \*\* outbound OGG needs Opus codec  

Size notes (outbound guidance; treat as planning ceiling): message up to **20MB**; **images 5MB**. Overview inbound note: **16MB** per message. T074 should enforce sensible caps and reject oversized/unsupported with Portuguese copy.

### Product mapping for WineAI

| Inbound | T074 handling |
|---------|----------------|
| `image/jpeg`, `image/png` (+ jpeg variants) | Download → multimodal Claude + optional `Body` caption |
| Audio MIME above (voice notes often OGG/Opus or MPEG) | Download → STT → text into existing IA path |
| PDF / video / docs / sticker / contact | Unsupported reply (non-goal for v1) |
| `NumMedia=0` | Existing text-only path |
| `NumMedia≥1` and empty `Body` | Must still enter domain (today’s bug) |

### Docs checklist

- [x] Twilio inbound media fields (`NumMedia`, `MediaUrl{N}`, `MediaContentType{N}`)
- [x] Twilio media download authentication (Basic Auth; follow redirect)
- [x] Supported WhatsApp media types / size limits (guidance + overview)
- [ ] Claude multimodal image input constraints (size, MIME) — still open
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
| EW-00 | Expand this SDD with normative EW-01… after STT provider + Claude multimodal constraints are chosen (ADR if new dep). | `docs/specs/sdd/T074-inbound-whatsapp-media-sdd.md`, optional ADR |

*(Implementation EW rows deferred until STT/vision choices land.)*

## Related

- [WhatsApp quickstart](https://www.twilio.com/docs/whatsapp/quickstart) (text only)
- [Send/receive media (Python)](https://www.twilio.com/docs/whatsapp/tutorial/send-and-receive-media-messages-whatsapp-python)
- [Webhook request parameters](https://www.twilio.com/docs/messaging/guides/webhook-request)
- [WhatsApp media guidance](https://www.twilio.com/docs/whatsapp/guidance-whatsapp-media-messages)
- [Media resource (auth)](https://www.twilio.com/docs/messaging/api/media-resource)
- [ROADMAP-TASKS.md](../../ROADMAP-TASKS.md) T074
- [T032-async-webhook-replies-sdd.md](./T032-async-webhook-replies-sdd.md)
- [operations/WHATSAPP-COMPLIANCE.md](../../operations/WHATSAPP-COMPLIANCE.md)
- [operations/DATA-RETENTION.md](../../operations/DATA-RETENTION.md)

## Revision history

| Date | Change |
|------|--------|
| 2026-11-18 | Initial draft — roadmap placeholder |
| 2026-11-18 | Attached Twilio media research from quickstart + sibling docs (fields, auth, MIME, sizes) |
