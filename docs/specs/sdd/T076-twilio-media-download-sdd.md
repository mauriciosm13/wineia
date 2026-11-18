# SDD — Twilio media download (T076)

**Status:** implemented  

**Task:** [T076](../../ROADMAP-TASKS.md) · parent [T074](./T074-inbound-whatsapp-media-sdd.md) · depends **T075**  
**Comparison contract:** this Expected work list is what the reviewer checks against [T076-builder-report.md](./T076-builder-report.md).

## Problem

`MediaUrl0` requires authenticated fetch; bytes must not be trusted blindly (size/MIME).

## Goals

- Infrastructure client: `GET MediaUrl0` with HTTP Basic Auth (`TWILIO_ACCOUNT_SID` + `TWILIO_AUTH_TOKEN`); follow 307 to CDN.
- Enforce MIME allowlist for image/audio (T074 research) and max size caps.
- Return bytes + content-type to domain; on failure send a distinct Portuguese reply (full ops wording polish may land in T079).
- Domain must not import infrastructure: inject a `media_downloader` callable from the handler.

## Non-goals

- STT / vision (T077 / T078).
- Long-term blob storage.
- Outbound media; payments T040–T043.
- Changing text-only behavior when `NumMedia=0`.

## Decisions (orchestrator defaults)

| Topic | Decision |
|-------|----------|
| Auth | HTTP Basic Auth with `TWILIO_ACCOUNT_SID` + `TWILIO_AUTH_TOKEN`; `allow_redirects=True` (follow 307 CDN) |
| Image MIME allowlist | `image/jpeg`, `image/jpg`, `image/png` |
| Audio MIME allowlist | `audio/ogg`, `audio/opus`, `audio/amr`, `audio/3gpp`, `audio/aac`, `audio/mpeg`, `audio/mp4` |
| Unsupported (v1) | webp stickers, PDF, video, docs, contacts → Portuguese unsupported copy |
| Max size | Images **5 MiB**; audio **16 MiB** (Twilio inbound overview ceiling); reject when declared or streamed size exceeds |
| HTTP client | `requests` (already in requirements); stream read with hard byte cap |
| After successful download | Domain holds bytes for T077/T078; media-only still fails closed with Portuguese “not processed yet” until those slices (no silent ignore). Download/MIME failures use distinct Portuguese strings. |

## Behavior

### Core allowlist / caps

Constants (or helpers) in `core` document allowed MIME sets and byte caps used by infrastructure and domain validation.

### Infrastructure `download_twilio_media(url, ...)`

1. Require non-empty URL, account SID, auth token.
2. `GET` with Basic Auth; follow redirects; timeout from `TWILIO_TIMEOUT`.
3. Stream body; abort if bytes exceed the cap for the effective MIME (response `Content-Type` preferred; else caller-provided webhook MIME).
4. Return `{"content": bytes, "content_type": str, "size": int}`.
5. Raise a small typed error (e.g. `TwilioMediaDownloadError`) on HTTP failure, missing credentials, oversize, or empty body.

### Domain

When media-only (no text) and `inbound_media` present:

1. If webhook `content_type` not in allowlist → `message_sender(MEDIA_UNSUPPORTED_MESSAGE)`; return `media_unsupported`; no download; no IA; no counter increment.
2. Else if `media_downloader` missing or `url` missing → existing `MEDIA_UNAVAILABLE_MESSAGE` / `media_unprocessable`.
3. Else call `media_downloader(url)` (injectable). On download error → `MEDIA_DOWNLOAD_FAILED_MESSAGE` / `media_download_failed`.
4. On success → still no IA until T077/T078; send `MEDIA_UNAVAILABLE_MESSAGE`; return `media_downloaded` (includes size/content_type for tests; **do not** persist raw bytes to Datastore).

Text path unchanged. Entitlement gate still runs before media handling (same as T075).

### Handler

Wire `media_downloader` in `_create_dependencies` to the infrastructure client. Pass into `process_incoming_message`.

## Expected work

The builder implements only these items. The reviewer marks each **match**, **gap**, or **extra**.

| ID | Must be true when the work is done | Where |
|----|-------------------------------------|--------|
| EW-01 | Core defines image/audio MIME allowlists and max byte caps (image 5 MiB, audio 16 MiB) plus a helper to classify/validate a MIME against those rules. | `core/` (e.g. config or `core/utils/twilio_media.py`) |
| EW-02 | Infrastructure `download_twilio_media` GETs the URL with HTTP Basic Auth (`TWILIO_ACCOUNT_SID` + `TWILIO_AUTH_TOKEN`), follows redirects, streams with a hard size cap, returns `{content, content_type, size}`. | `infrastructure/external/twilio_media_client.py` |
| EW-03 | Download raises a typed error for missing credentials/URL, non-success HTTP, oversize, or empty body. Unit tests use fakes/mocks (no live Twilio). | same + tests |
| EW-04 | `process_incoming_message` accepts optional `media_downloader`. Media-only + unsupported MIME → Portuguese unsupported reply, no download/IA/increment. | `domain/services/messaging_service.py` |
| EW-05 | Media-only + allowed MIME: calls `media_downloader(url)`; download failure → Portuguese download-failed reply; success → `media_downloaded` status and Portuguese unavailable-for-processing reply (until T077/T078); no IA; no counter increment; no Datastore blob write. | messaging_service + domain tests |
| EW-06 | `whatsapp_handler` injects infrastructure download callable as `media_downloader`. Text-only path unchanged. Domain does not import infrastructure. | `api/handlers/whatsapp_handler.py` |
| EW-07 | Unit tests cover: allowlist helper; download success / oversize / auth failure (mocked HTTP); domain unsupported / download fail / download success paths; text-only regression. | `tests/` |
| EW-08 | Only after EW-01–EW-07 and EW-09 hold: `ROADMAP-TASKS.md` checks **T076**; this SDD status `implemented`; `INDEX.md` T076 `implemented`. Do not check T077–T079 or payments. | those files |
| EW-09 | Diff does not implement STT, vision, payments, or long-term media persistence. Domain/core coverage ≥ 95%. pytest, ruff, and `python quality/check_import_style.py` pass. | whole diff |

## Builder report

After implementation, write `docs/specs/sdd/T076-builder-report.md` with EW → files mapping, files touched, and verification commands.

## Reviewer comparison

Read this file, the builder report, and the diff. Return only EW match/gap lines, extras, bugs, verdict accept/reject. Do not implement.

## Related

- [Media resource auth](https://www.twilio.com/docs/messaging/api/media-resource)
- [T074](./T074-inbound-whatsapp-media-sdd.md)
- [T075](./T075-twilio-media-parser-sdd.md)

## Revision history

| Date | Change |
|------|--------|
| 2026-11-18 | Initial draft slice |
| 2026-11-18 | Expand Expected work EW-01–EW-09; caps MIME/auth defaults |
| 2026-11-18 | Status `implemented` after EW-01–EW-09 hold |
