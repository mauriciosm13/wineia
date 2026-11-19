# SDD — Inbound audio STT (T077)

**Status:** implemented  
**Task:** [T077](../../ROADMAP-TASKS.md) · parent [T074](./T074-inbound-whatsapp-media-sdd.md) · depends **T076**  
**Comparison contract:** this Expected work list is what the reviewer checks against [T077-builder-report.md](./T077-builder-report.md).

## Problem

Voice notes arrive as audio MIME; after T076 download, `_handle_media_only` still sends `MEDIA_UNAVAILABLE_MESSAGE`. Product IA path is text-only.

## Goals

- Transcribe inbound WhatsApp audio → Portuguese text → existing `ia_service.generate_response`.
- Count as **one** on-demand IA turn after a successful product reply (STT alone does not increment).
- Apply Claude daily budget at the Claude call site (existing `IAService` path).
- Fail closed with Portuguese copy if STT fails or transcript is empty.
- Clean Architecture: domain never imports infrastructure; inject STT callable from the handler.

## Non-goals

- Image vision (T078).
- Outbound media; video/PDF/sticker processing; long-term Datastore blob storage.
- Payments T040–T043.
- Changing text-only behavior when `NumMedia=0`.
- STT for non-empty `Body` + audio (existing text IA path wins when Body has text).

## Decisions (locked)

| Topic | Decision |
|-------|----------|
| Claude for STT? | **No.** Anthropic Messages API accepts text/image only (no audio content block). |
| STT provider | **OpenAI Audio Transcriptions** (`POST /v1/audio/transcriptions`) — [ADR 0006](../../adrs/0006-openai-whisper-stt.md). |
| New pip dependency | **None.** Call the HTTP API with existing `requests`. |
| Model | `whisper-1` (stable multipart; language=`pt` for pt-BR). |
| Language | ISO-639-1 `pt` (Portuguese / pt-BR target). |
| Auth / config | `OPENAI_API_KEY` from env, with optional `config.json` key fallback for local (same pattern family as Anthropic key). |
| Compatible MIME for STT attempt | Whisper-supported subset of the T076 audio allowlist: `audio/ogg`, `audio/opus`, `audio/mpeg`, `audio/mp4`, `audio/aac`. Map filename extension for multipart (`ogg`/`mp3`/`mp4`/`m4a`). |
| Unsupported for STT (still allowed download) | `audio/amr`, `audio/3gpp` → Portuguese STT-failed copy (fail closed; no silent ignore). |
| Quota | One on-demand increment only after successful IA reply send (same as text). STT failure / empty transcript → no increment. |
| Claude budget | Unchanged: applied inside `IAService.generate_response`. Budget exceeded → existing `SERVICE_UNAVAILABLE_MESSAGE` / `budget_exceeded`. |
| Image after download (this slice) | Still Portuguese unavailable / no vision until T078. |

## Behavior

### Infrastructure `transcribe_audio(content, content_type, ...)`

1. Require non-empty bytes and configured API key.
2. Reject STT-incompatible MIME with typed error (caller maps to Portuguese failure).
3. `POST` multipart to OpenAI transcriptions with `model=whisper-1`, `language=pt`, file bytes + derived filename.
4. Return stripped transcript string.
5. Raise typed error on HTTP/API failure, missing key, empty body, or empty transcript.

### Domain

When media-only (no text) and download succeeds:

1. Classify MIME (`core` helper).
2. **Audio:** call injectable `audio_transcriber(content, content_type)`. On failure / empty → Portuguese STT-failed reply; status `media_stt_failed`; no IA; no counter increment.
3. On transcript success → same product path as text: `ia_service.generate_response(customer, transcript)` → `message_sender` → increment `messages_sent_today` + `last_message_at` → return `processed`.
4. **Image:** keep T076 unavailable-for-processing reply until T078 (`media_downloaded` + `MEDIA_UNAVAILABLE_MESSAGE`); no IA; no increment.
5. Missing `audio_transcriber` on audio path → Portuguese unavailable (or STT-failed) reply; no silent ignore.

Text-only path unchanged. Entitlement gate still runs before media handling.

### Handler

Wire `audio_transcriber` in `_create_dependencies` to the infrastructure STT client. Pass into `process_incoming_message`.

## Expected work

The builder implements only these items. The reviewer marks each **match**, **gap**, or **extra**.

| ID | Must be true when the work is done | Where |
|----|-------------------------------------|--------|
| EW-01 | ADR documents why Claude cannot STT and chooses OpenAI transcriptions via `requests` (no new pip dep), model `whisper-1`, language `pt`. | `docs/adrs/0006-openai-whisper-stt.md` |
| EW-02 | Infrastructure `transcribe_audio` POSTs multipart to OpenAI `/v1/audio/transcriptions` with API key, returns stripped text; raises typed error for missing key/bytes, incompatible MIME, HTTP/API failure, or empty transcript. Unit tests use fakes/mocks (no live OpenAI). | `infrastructure/external/` + tests |
| EW-03 | Core (or shared helper) can identify which allowed audio MIME types are STT-compatible vs fail-closed without calling OpenAI. | `core/` |
| EW-04 | `process_incoming_message` accepts optional `audio_transcriber`. Media-only audio + successful download + STT + IA → Portuguese product reply, counter +1, status `processed`. Domain does not import infrastructure. | `domain/services/messaging_service.py` |
| EW-05 | STT failure / empty transcript / missing transcriber / STT-incompatible audio MIME → distinct Portuguese fail-closed reply; no counter increment; no silent ignore. | messaging_service + domain tests |
| EW-06 | Media-only **image** after download still returns unavailable-for-processing behavior (no vision in this slice). Text-only path unchanged. | messaging_service + tests |
| EW-07 | `whatsapp_handler` injects STT callable as `audio_transcriber`. Claude budget still applied only at IA generation (existing path). | `api/handlers/whatsapp_handler.py` |
| EW-08 | Unit tests cover: STT success → IA; STT fail; empty transcript; incompatible audio MIME; image still unavailable; text regression; mocked OpenAI HTTP. | `tests/` |
| EW-09 | Only after EW-01–EW-08 and EW-10 hold: `ROADMAP-TASKS.md` checks **T077**; this SDD status `implemented`; `INDEX.md` T077 `implemented`. Do not check T078–T079 or payments. | those files |
| EW-10 | Diff does not implement vision (T078), payments, or long-term media persistence. Domain/core coverage ≥ 95%. pytest, ruff, and `python quality/check_import_style.py` pass. | whole diff |

## Builder report

After implementation, write `docs/specs/sdd/T077-builder-report.md` with EW → files mapping, files touched, and verification commands.

## Reviewer comparison

Read this file, the builder report, and the diff. Return only EW match/gap lines, extras, bugs, verdict accept/reject. Do not implement.

## Related

- [ADR 0006](../../adrs/0006-openai-whisper-stt.md)
- [T074](./T074-inbound-whatsapp-media-sdd.md)
- [T076](./T076-twilio-media-download-sdd.md)
- [T078](./T078-inbound-image-vision-sdd.md)

## Revision history

| Date | Change |
|------|--------|
| 2026-11-18 | Initial draft slice |
| 2026-11-18 | Expand Expected work EW-01–EW-10; lock OpenAI Whisper via requests + ADR 0006 |
