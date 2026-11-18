# SDD — Twilio media download (T076)

**Status:** draft  
**Task:** [T076](../../ROADMAP-TASKS.md) · parent [T074](./T074-inbound-whatsapp-media-sdd.md) · depends **T075**

## Problem

`MediaUrl0` requires authenticated fetch; bytes must not be trusted blindly (size/MIME).

## Goals

- Infrastructure client: `GET MediaUrl0` with HTTP Basic Auth (`TWILIO_ACCOUNT_SID` + `TWILIO_AUTH_TOKEN` or API key); follow 307 to CDN.
- Enforce MIME allowlist for image/audio (T074 research) and a max size cap.
- Return bytes + content-type to domain; on failure surface a Portuguese error path (wired fully in T079).

## Non-goals

- STT / vision (T077 / T078).
- Long-term blob storage.

## Related

- [Media resource auth](https://www.twilio.com/docs/messaging/api/media-resource)
- [T074](./T074-inbound-whatsapp-media-sdd.md)

## Revision history

| Date | Change |
|------|--------|
| 2026-11-18 | Initial draft slice |
