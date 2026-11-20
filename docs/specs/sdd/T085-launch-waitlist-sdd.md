# SDD — Launch waitlist / pré-lista (T085)

**Status:** implemented  
**Task:** [T085](../../ROADMAP-TASKS.md)  
**Commercial-launch:** Phase 4/6 adjacent (lead capture before paid checkout)

## Problem

Marketing (Instagram, site) needs a **pré-lista** of interested people so ops can later send **discounted Asaas checkout links**. Existing `POST /customers/pre-sale` is an **operator-authenticated** funnel into Customer activation — not a public waitlist for launch discounts.

## Goals

1. Public API for the frontend waitlist form (no `JOB_INTERNAL_SECRET` on the public POST).
2. Persist leads with: WhatsApp phone, name, email, birth date (age checks), `created_at`, `updated_at`.
3. Later (ops): list/export leads and send Asaas payment links with discount (out of band or follow-up slice).
4. LGPD: privacy/terms notice (reuse T050 pattern where sensible); retention/export/erase story.

## Non-goals

- Auto-sending WhatsApp discount links in the first slice (manual/ops OK).
- Replacing pre-sale (`/customers/pre-sale`) — keep both; document when to use which.
- Payment capture (Asaas) — T044.

## Fields (entity)

| Field | Notes |
|-------|--------|
| `phone` / WhatsApp | E.164 normalized; unique key candidate |
| `name` | Required |
| `email` | Required; normalize lower-case |
| `birth_date` | ISO date; used to validate minimum age (default 18; env-tunable) |
| `created_at` | Set on insert |
| `updated_at` | Set on insert and update |
| Optional later | `discount_code`, `checkout_sent_at`, `source` (instagram/site) |

## API sketch

| Method | Path | Auth | Behavior |
|--------|------|------|----------|
| `POST` | `/waitlist` or `/leads/waitlist` | Public + rate limit | Upsert by phone or email; reject under-age; return 201/200 |
| `GET` | `/waitlist` (list) | `JOB_INTERNAL_SECRET` | Operator list/export for sending discount links |
| `PATCH` | `/waitlist/{id}` | Operator | Update contact fields; bump `updated_at` |

Exact paths finalized in Expected Work; prefer Clean Architecture (handler → domain → Datastore repo).

## Distinction vs pre-sale

| | Waitlist (T085) | Pre-sale (existing) |
|--|-----------------|---------------------|
| Audience | Launch / discount campaign | Operator-managed lead → customer |
| Auth on create | Public (rate-limited) | `JOB_INTERNAL_SECRET` |
| Outcome | Lead for later checkout link | Can activate to Customer |

## Slices

| Task | Scope |
|------|--------|
| **T086** | Domain model + Datastore repository + age validation |
| **T087** | Public `POST` + rate limit + privacy notice |
| **T088** | Operator list/export + docs for sending discounted Asaas links |

## Acceptance criteria (epic)

- [x] Frontend can POST a lead with the required fields
- [x] Under-age rejected with clear Portuguese error
- [x] Ops can list leads to message discount checkout links
- [x] No secrets in git; PRODUCTION route table updated

## Related

- [T086](./T086-waitlist-model-sdd.md) · [T087](./T087-waitlist-public-post-sdd.md) · [T088](./T088-waitlist-operator-export-sdd.md)
- [T044 Asaas webhook](./T044-asaas-payment-webhook-sdd.md) · [T050 privacy](./T050-privacy-terms-opt-in-sdd.md)
- Ops: [WAITLIST-DISCOUNT-LINKS.md](../../operations/WAITLIST-DISCOUNT-LINKS.md)

## Revision history

| Date | Change |
|------|--------|
| 2026-11-20 | Initial epic from product ask (Instagram + site pré-lista) |
| 2026-11-20 | Implemented via T086–T088 (`POST`/`GET /waitlist`, phone upsert) |
