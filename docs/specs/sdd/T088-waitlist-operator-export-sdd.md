# SDD — Waitlist operator list / discount send prep (T088)

**Status:** implemented  
**Task:** [T088](../../ROADMAP-TASKS.md) · parent [T085](./T085-launch-waitlist-sdd.md) · depends **T086–T087**

## Goals

- Authenticated operator `GET /waitlist` (job secret) — list/export JSON for ops.
- Document runbook: export leads → create Asaas payment links with discount → send via WhatsApp/email (manual MVP).
- Optional fields later: `checkout_sent_at`, `discount_code` (may be a follow-up if not in T086).

## Acceptance criteria

- [x] Operator-only list works with job secret
- [x] Short ops runbook in `docs/operations/` or LAUNCH-CHECKLIST section
- [x] LGPD note: waitlist PII in DATA-RETENTION

## Related

- [T085](./T085-launch-waitlist-sdd.md) · [T044](./T044-asaas-payment-webhook-sdd.md)
- [WAITLIST-DISCOUNT-LINKS.md](../../operations/WAITLIST-DISCOUNT-LINKS.md)

## Revision history

| Date | Change |
|------|--------|
| 2026-11-20 | Initial draft |
| 2026-11-20 | Implemented: `GET /waitlist` + ops runbook + DATA-RETENTION |
