# SDD — Inbound image vision (T078)

**Status:** implemented  
**Task:** [T078](../../ROADMAP-TASKS.md) · parent [T074](./T074-inbound-whatsapp-media-sdd.md) · depends **T076** / **T077**  
**Comparison contract:** this Expected work list is what the reviewer checks against [T078-builder-report.md](./T078-builder-report.md).

## Problem

Customers send bottle/label photos; after T076 download, media-only images still get `MEDIA_UNAVAILABLE_MESSAGE`. Claude path is text-only.

## Goals

- Multimodal Claude for `image/jpeg` / `image/png` (+ `image/jpg`).
- Optional caption from inbound `Body` included in the prompt.
- Unsupported MIME already has Portuguese reply (T075/T076); keep that.
- Entitlements + Claude daily budget still apply (one on-demand turn per successful reply).
- Fail closed with Portuguese copy if vision fails.

## Non-goals

- Audio STT changes beyond preserving T077 behavior.
- Outbound media; video/PDF/sticker/GIF/WebP processing (GIF/WebP not in T076 allowlist).
- Long-term Datastore blob storage; payments T040–T043.
- New pip dependencies (use existing `anthropic`).

## Decisions (locked)

| Topic | Decision |
|-------|----------|
| Provider | Claude multimodal via `ClaudeClient` / `IAService` (existing Anthropic stack). |
| MIME | `image/jpeg`, `image/jpg`, `image/png`. Map `image/jpg` → API `image/jpeg`. |
| Size cap | T076 image max **5 MiB** raw bytes (under Anthropic ~10 MiB base64-encoded API ceiling). |
| Encoding | Base64 image block in Messages API (`type=image`, `source.type=base64`). |
| Caption | When inbound image is present, use vision path; `Body` (possibly empty) is the optional caption. Prefer vision over text-only when an allowed image is attached. |
| Prompt | Same Gastón sommelier rules as text IA; user content describes the photo + optional caption as data, not instructions. |
| Quota | One on-demand increment after successful vision reply send. Vision failure → no increment. |
| Claude budget | Apply at Claude call site via existing `IAService._generate_with_budget`. |
| Fail closed | Vision/API failure or missing image bytes → Portuguese vision-failed copy. |
| Audio | T077 path unchanged (media-only audio → STT → text IA). |

## Behavior

### Infrastructure `ClaudeClient.generate`

Accept optional image payload(s): when present, build multimodal `messages[].content` with image block(s) then text. Text-only callers unchanged.

### Domain `IAService.generate_vision_response(customer, image_bytes, content_type, caption=None)`

1. Sanitize caption text (empty → default Portuguese instruction to analyze the wine/label photo).
2. Call budget-gated generate with system prompt (Gastón rules) + image + user text.
3. Validate output like text path.

### Domain messaging

1. Entitlement / cancel / reset unchanged.
2. If inbound media is an **allowed image**: download (same as T076) → `generate_vision_response` with caption=`Body` → sender → increment → `processed`.
3. Download failure / unsupported MIME: existing Portuguese paths.
4. Vision failure: `MEDIA_VISION_FAILED_MESSAGE` / `media_vision_failed`; no increment.
5. Media-only audio: keep T077 STT path.
6. Text without image: existing text IA path.

### Handler

No new DI required beyond T076/T077 (vision uses `ia_service`). Pass caption via existing `message` / `inbound_media` args.

## Expected work

The builder implements only these items. The reviewer marks each **match**, **gap**, or **extra**.

| ID | Must be true when the work is done | Where |
|----|-------------------------------------|--------|
| EW-01 | `ClaudeClient.generate` supports optional base64 image input (JPEG/PNG) while preserving text-only callers. Unit tests mock Anthropic (no live API). | `infrastructure/external/claude_client.py` + tests |
| EW-02 | `IAService.generate_vision_response` builds Gastón multimodal prompt with optional caption, routes through Claude daily budget helper, returns validated text. | `domain/services/ia_service.py` + tests |
| EW-03 | Media path: allowed inbound image → download → vision → product reply → counter +1 → `processed`. Optional `Body` caption included. Domain does not import new infrastructure modules for vision. | `domain/services/messaging_service.py` |
| EW-04 | Vision failure / missing image bytes → distinct Portuguese fail-closed reply; no counter increment; no silent ignore. Unsupported MIME / download failure paths unchanged in spirit. | messaging_service + tests |
| EW-05 | Media-only audio STT path (T077) still works. Text-only without image unchanged. | messaging_service + tests |
| EW-06 | Unit tests cover: vision success (+ caption); vision fail; image+caption prefers vision; audio STT regression; text-only regression. | `tests/` |
| EW-07 | Only after EW-01–EW-06 and EW-08 hold: `ROADMAP-TASKS.md` checks **T078**; this SDD status `implemented`; `INDEX.md` T078 `implemented`. Do not check T079 or payments. | those files |
| EW-08 | Diff does not implement payments or long-term media persistence. Domain/core coverage ≥ 95%. pytest, ruff, and `python quality/check_import_style.py` pass. | whole diff |

## Builder report

After implementation, write `docs/specs/sdd/T078-builder-report.md` with EW → files mapping, files touched, and verification commands.

## Reviewer comparison

Read this file, the builder report, and the diff. Return only EW match/gap lines, extras, bugs, verdict accept/reject. Do not implement.

## Related

- [T074](./T074-inbound-whatsapp-media-sdd.md)
- [T076](./T076-twilio-media-download-sdd.md)
- [T077](./T077-inbound-audio-stt-sdd.md)
- Anthropic Vision docs (JPEG/PNG; ~10 MiB base64 API; WineAI uses 5 MiB raw from T076)

## Revision history

| Date | Change |
|------|--------|
| 2026-11-18 | Initial draft slice |
| 2026-11-18 | Expand Expected work EW-01–EW-08; lock Claude multimodal + caption + 5 MiB |
