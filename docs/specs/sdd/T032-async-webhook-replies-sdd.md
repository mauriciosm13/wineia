# SDD — Full async webhook replies via queue (T032)

**Status:** draft  
**Task:** [T032](../../ROADMAP-TASKS.md)

## Problem

WhatsApp webhook may block on Claude + Twilio sync path.

## Goals

Enqueue outbound reply via Cloud Tasks send_message; return 200 quickly; worker sends text.

## Acceptance criteria

No regression on signature validation; document Twilio retry behavior; optional idempotency key later.

## Related

- `docs/ROADMAP.md M2`
- `domain/services/messaging_service.py`

## Revision history

| Date | Change |
|------|--------|
| 2026-11-10 | Initial SDD |
