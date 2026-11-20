# SDD — Inbound media ops + tests (T079)

**Status:** implemented  
**Task:** [T079](../../ROADMAP-TASKS.md) · parent [T074](./T074-inbound-whatsapp-media-sdd.md) · depends **T075–T078**

## Goals

- Document inbound media in `PRODUCTION.md`, `WHATSAPP-COMPLIANCE.md`, and ephemeral handling in `DATA-RETENTION.md` (LGPD).
- Unit tests: media-only routing, download failure copy, unsupported MIME copy, entitlements unchanged for text.
- Confirm no long-term Datastore storage of raw media blobs.

## Acceptance criteria

- [x] Ops docs updated (ephemeral media, no long-term blob storage, entitlements/budget on media turns; runtime providers Claude vision + OpenAI Whisper STT as on `main`).
- [x] Threat-model residual note for large-media DoS / size caps (T076).
- [x] Unit tests for media-only routing, download failure copy, unsupported MIME copy; text-only entitlements still green.
- [x] Coverage gate still passes.

## Related

- [T074](./T074-inbound-whatsapp-media-sdd.md)

## Revision history

| Date | Change |
|------|--------|
| 2026-11-18 | Initial draft slice |
| 2026-11-20 | Implemented: ops docs + strengthened unit tests; marked done |
