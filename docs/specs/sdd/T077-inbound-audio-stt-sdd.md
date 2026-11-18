# SDD — Inbound audio STT (T077)

**Status:** draft  
**Task:** [T077](../../ROADMAP-TASKS.md) · parent [T074](./T074-inbound-whatsapp-media-sdd.md) · depends **T076**

## Problem

Voice notes arrive as audio MIME; product IA path is text-only today.

## Goals

- Choose STT provider (ADR if new dependency).
- Transcribe inbound audio → Portuguese text → existing `process_incoming_message` / `ia_service.generate_response`.
- Count as one on-demand IA turn (same entitlements + Claude budget gates).
- Fail closed with Portuguese copy if STT fails.

## Open decisions

- [ ] STT provider (Claude? Google? Whisper API? other)
- [ ] ADR number if new pip dependency

## Related

- [T074](./T074-inbound-whatsapp-media-sdd.md) audio MIME list

## Revision history

| Date | Change |
|------|--------|
| 2026-11-18 | Initial draft slice |
