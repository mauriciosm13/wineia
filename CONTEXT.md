# CONTEXT — WineAI (wineia)

> Roadmap handoff after Asaas + waitlist planning (2026-11-20).

## Primary objectives (next product work)

1. **Payments (Asaas)** — T040 → T041 → T044 (webhook) → T043 as needed. Instagram → direct Asaas checkout; backend activates via webhook.
2. **Launch waitlist** — T085–T088: public pré-lista (phone, name, email, birth_date, created_at, updated_at) for later discount links.
3. **T084** — still open for `XAI_API_KEY` Secret Manager / ops (Grok code already on `main`).

## Locked decisions

| Topic | Decision |
|-------|----------|
| Checkout UX | Instagram → Asaas checkout direct (no intermediate landing required) |
| Provider intent | Asaas (ADR 0003 Accept in T040) |
| Waitlist vs pre-sale | Waitlist = public launch leads; pre-sale = existing operator funnel |

## Branch (this docs PR)

`cursor/asaas-waitlist-roadmap-afd2`
