# SDD — One Claude per broadcast slot (T023)

**Status:** implemented  
**Task:** [T023](../../ROADMAP-TASKS.md)

## Canonical specification

This SDD is summarized here. Full normative detail: [`../recommendation-broadcast-slot.md`](../recommendation-broadcast-slot.md).

## Problem

send_recommendations called Claude per customer.

## Goals

Single generate_recommendation per job; fan-out same body.

## Acceptance criteria

See recommendation-broadcast-slot spec.

## Related

- `../recommendation-broadcast-slot.md`

## Revision history

| Date | Change |
|------|--------|
| 2026-11-10 | Initial SDD |
