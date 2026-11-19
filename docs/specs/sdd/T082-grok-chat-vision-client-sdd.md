# SDD — Grok chat + vision client (T082)

**Status:** draft  
**Task:** [T082](../../ROADMAP-TASKS.md) · parent [T080](./T080-grok-ia-stack-sdd.md) · depends **T081**

## Goals

- Add `infrastructure/external/` Grok client for **text** and **image** (JPEG/PNG base64 or URL per xAI docs), mirroring the current Claude surface used by `ia_service` (generate text; generate with optional image for inbound vision).
- Wire `ia_service` / composition root to Grok as primary; keep domain free of HTTP/SDK imports.
- Prefer **`requests` + env `XAI_API_KEY`** (no new pip dep unless ADR says otherwise).
- Unit tests with mocked HTTP; no live xAI calls in CI.
- Preserve Gastón system prompts and Portuguese product behavior; only the transport/model changes.

## Non-goals

- STT (T083).
- Removing Anthropic from `requirements.txt` in the same PR if a rollback flag is still useful — may leave Claude client dead until a follow-up cleanup.

## Acceptance criteria

- [ ] On-demand text and image paths succeed in unit tests via Grok client fakes.
- [ ] Broadcast / suggestion paths that call Claude today go through the same IA abstraction (one generation per slot still holds — T023).
- [ ] Import style / Clean Architecture rules unchanged.

## Related

- [T080](./T080-grok-ia-stack-sdd.md) · [T078 vision](./T078-inbound-image-vision-sdd.md)

## Revision history

| Date | Change |
|------|--------|
| 2026-11-19 | Initial draft |
