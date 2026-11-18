# SDD — Inbound image vision (T078)

**Status:** draft  
**Task:** [T078](../../ROADMAP-TASKS.md) · parent [T074](./T074-inbound-whatsapp-media-sdd.md) · depends **T076**

## Problem

Customers send bottle/label photos; Claude path is text-only.

## Goals

- Multimodal Claude (or approved equivalent) for `image/jpeg` / `image/png` (+ documented variants).
- Optional caption from `Body` included in the prompt.
- Unsupported MIME (PDF, video, sticker, etc.): clear Portuguese “not supported” reply (no silent ignore).
- Entitlements + Claude daily budget still apply.

## Open decisions

- [ ] Claude multimodal size/MIME constraints for production
- [ ] Whether image turns share the same on-demand counter as text (default: yes)

## Related

- [T074](./T074-inbound-whatsapp-media-sdd.md)
- `infrastructure/external/claude_client.py`, `domain/services/ia_service.py`

## Revision history

| Date | Change |
|------|--------|
| 2026-11-18 | Initial draft slice |
