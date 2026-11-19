# SDD — ADR 0007 Grok provider choice (T081)

**Status:** implemented  
**Task:** [T081](../../ROADMAP-TASKS.md) · parent [T080](./T080-grok-ia-stack-sdd.md)

## Goals

- Write and accept **ADR 0007** documenting:
  - **Grok** (e.g. `grok-4.7`) for chat + image understanding (text+image in → text out).
  - **Grok Voice Transcribe** (REST `POST /v1/stt`, batch ~$0.10/hr) for inbound WhatsApp audio.
  - Rationale: single vendor, lower unit cost vs Claude Sonnet + Whisper for test/launch; multimodal without a second STT key.
- Update **ADR 0006** status to **Superseded by ADR 0007** (keep history; do not delete).
- Explicitly note: Claude Haiku may still be cheaper on tokens alone but does not unify STT; product chose Grok for all-in-one ops.

## Non-goals

- Implementing clients (T082/T083).
- Adding `xai-sdk` pip package unless ADR justifies it (default: HTTP + `requests`).

## Acceptance criteria

- [x] `docs/adrs/0007-xai-grok-ia-stack.md` exists and is Accepted (or Proposed with clear next step).
- [x] ADR 0006 header reflects superseded status + link to 0007.
- [x] INDEX / ROADMAP-TASKS T081 marked done after ADR lands.

## Related

- [T080](./T080-grok-ia-stack-sdd.md) · [ADR 0006](../../adrs/0006-openai-whisper-stt.md) · [ADR 0007](../../adrs/0007-xai-grok-ia-stack.md)

## Revision history

| Date | Change |
|------|--------|
| 2026-11-19 | Initial draft |
| 2026-11-19 | ADR 0007 accepted; ADR 0006 superseded; T081 done |
