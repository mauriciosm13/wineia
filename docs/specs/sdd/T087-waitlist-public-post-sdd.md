# SDD — Waitlist public POST (T087)

**Status:** implemented  
**Task:** [T087](../../ROADMAP-TASKS.md) · parent [T085](./T085-launch-waitlist-sdd.md) · depends **T086**

## Goals

- `POST /waitlist` (name TBD) for frontend; **no** job secret.
- Rate limit (reuse webhook-style IP limits or dedicated waitlist limits).
- Privacy/terms notice on response (T050-style URLs).
- Portuguese error copy for validation failures.

## Non-goals

- Operator GET/export (T088).

## Acceptance criteria

- [x] Handler thin; domain owns rules
- [x] Route tests + rate-limit coverage
- [x] PRODUCTION.md route row

## Related

- [T085](./T085-launch-waitlist-sdd.md) · [T012](./T012-webhook-rate-limit-sdd.md)

## Revision history

| Date | Change |
|------|--------|
| 2026-11-20 | Initial draft |
| 2026-11-20 | Implemented: public `POST /waitlist` + IP rate limit + privacy notice |
