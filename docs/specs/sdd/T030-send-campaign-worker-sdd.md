# SDD — POST /workers/send-campaign (T030)

**Status:** draft  
**Task:** [T030](../../ROADMAP-TASKS.md)

## Canonical specification

Normative acceptance tests and handler contract will live in `docs/specs/send-campaign-worker-sdd.md` when that spec merges; until then, this file is the task SDD.

## Problem

wine-campaigns queue targeted missing worker path.

## Goals

Worker mirrors send-message contract; internal auth; Twilio send.

## Acceptance criteria

Handler: `POST /workers/send-campaign` with job internal auth; payload mirrors send-message; queue `wine-campaigns`.

## Related

- `core/queues.py`
- `docs/DEPLOYMENT.md`

## Revision history

| Date | Change |
|------|--------|
| 2026-11-10 | Initial SDD |
