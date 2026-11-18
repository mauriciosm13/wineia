# SDD — Inbound media ops + tests (T079)

**Status:** draft  
**Task:** [T079](../../ROADMAP-TASKS.md) · parent [T074](./T074-inbound-whatsapp-media-sdd.md) · depends **T075–T078** (or land docs/tests as each slice merges)

## Goals

- Document inbound media in `PRODUCTION.md`, `WHATSAPP-COMPLIANCE.md`, and ephemeral handling in `DATA-RETENTION.md` (LGPD).
- Unit tests: media-only routing, download failure copy, unsupported MIME copy, entitlements unchanged for text.
- Confirm no long-term Datastore storage of raw media blobs.

## Acceptance criteria

- Ops docs updated; coverage gate still passes; threat-model note if residual risk (e.g. large media DoS — size caps from T076).

## Related

- [T074](./T074-inbound-whatsapp-media-sdd.md)

## Revision history

| Date | Change |
|------|--------|
| 2026-11-18 | Initial draft slice |
