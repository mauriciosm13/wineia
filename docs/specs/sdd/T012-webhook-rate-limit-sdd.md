# SDD — Webhook abuse rate limits (T012)

**Status:** implemented  
**Task:** [T012](../../ROADMAP-TASKS.md)

## Canonical specification

This SDD is summarized here. Full normative detail: [`../webhook-rate-limit.md`](../webhook-rate-limit.md).

## Problem

Public webhook could be abused for cost/DoS.

## Goals

Sliding window per IP and per phone on POST /webhook/whatsapp; 429.

## Acceptance criteria

See canonical spec; defaults 120/min IP, 30/min phone.

## Related

- `../webhook-rate-limit.md`

## Revision history

| Date | Change |
|------|--------|
| 2026-11-10 | Initial SDD |
