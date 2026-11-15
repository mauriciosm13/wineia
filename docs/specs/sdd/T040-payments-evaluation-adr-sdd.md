# SDD — Payments evaluation + ADR 0003 (T040)

**Status:** implemented  
**Task:** [T040](../../ROADMAP-TASKS.md)  
**Comparison contract:** this Expected work list is what the reviewer checks against [T040-builder-report.md](./T040-builder-report.md).

## Problem

Payment provider is undecided. COMMERCIAL-LAUNCH #53 blocks billing webhooks (T042). `payments-evaluation.md` and ADR 0003 still say TBD; `commercial.md` and `decision.md` still treat the provider as unknown. Without a chosen API, subscription activation stays manual and webhook design cannot start.

## Goals

- Complete a scored Brazil provider comparison (cost 40%, ease 35%, recurrence 25%) for Mercado Pago, Stripe, Asaas, and PagBank.
- Accept ADR 0003 with **Asaas** as the provider and **Mercado Pago** as runner-up.
- Update commercial and decision docs so the provider is no longer TBD.
- Mark CL #53 and T040 complete; set this SDD and INDEX to `implemented`.
- Keep the diff docs-only: no T041 fields, no payment routes, no runtime payment code.

## Non-goals

- Implementing T041 subscription state fields.
- Implementing T042 `POST /webhooks/payments` or any webhook handler.
- Implementing T043 manual provisioning runbook body.
- Live sandbox API calls, fee scraping, or MDR contracts signed in this task.
- Checking COMMERCIAL-LAUNCH #63 (LGPD subprocessors checklist) — naming Asaas in `commercial.md` is enough here.
- New pip dependencies. `docs/MVP_SCOPE.md`.
- T004 GitHub branch protection.

**Ops prerequisite for T042 (not a T040 deliverable):** after ADR acceptance, ops must run a CNPJ sandbox smoke of one Asaas subscription plus one webhook delivery in a non-prod project before webhook code lands. Document that gate in evaluation + ADR; do not perform it in T040.

## Behavior

### Evaluation weights

| Criterion | Weight | What it measures |
|-----------|--------|------------------|
| Cost | 40% | Expected MDR / Pix / subscription fees for BR SaaS (directional; live rates need ops verify) |
| Ease | 35% | Docs, sandbox, CNPJ onboarding, webhook DX, BR methods (Pix + card) |
| Recurrence | 25% | Native subscription/recurring billing fit for Entry / Superior / add-on |

Score each provider 1–10 per criterion. Weighted total = `cost×0.40 + ease×0.35 + recurrence×0.25`. Highest total wins.

### Decision

| Role | Provider |
|------|----------|
| Chosen | **Asaas** |
| Runner-up | Mercado Pago |

Rationale summary: Asaas is recurrence-first for Brazilian SaaS, supports Pix + card, and exposes webhooks suitable for tier activation. Mercado Pago remains the fallback if Asaas onboarding or pricing fails ops verification.

### Doc outcomes

| Doc | After T040 |
|-----|------------|
| `payments-evaluation.md` | Status chosen; scored table; prose; sandbox = T042 ops prereq |
| ADR 0003 | **Accepted**; Asaas; consequences; alternatives |
| `commercial.md` | Payments + subprocessors name Asaas |
| `decision.md` | Payment gap records Asaas; manual until T042 |
| CL #53, ROADMAP-TASKS T040, INDEX | Checked / `implemented` |

## Expected work

The builder implements only these items. The reviewer marks each **match**, **gap**, or **extra**.

| ID | Must be true when the work is done | Where |
|----|-------------------------------------|--------|
| EW-01 | `payments-evaluation.md` has a scored comparison table for Mercado Pago, Stripe, Asaas, and PagBank using weights **cost 40%**, **ease 35%**, **recurrence 25%** (1–10 scores + weighted totals). Prose justifies scores covering CNPJ availability, Pix + card, recurring billing, webhooks/idempotency, and sandbox. Status reflects **Asaas chosen**, Mercado Pago runner-up. Notes that live MDR/fees need ops verification before production cutover, and that a sandbox subscription+webhook smoke is an **ops prerequisite for T042**, not a T040 code deliverable. Requirements table still covers recurring billing, webhooks + idempotency, Pix + card, and sandbox. | `docs/payments-evaluation.md` |
| EW-02 | ADR 0003 status is **Accepted**. Decision names **Asaas**. Consequences include at least: webhook route shape deferred to T042; subprocessors list update; LGPD DPA appendix; manual provisioning continues until T042. Alternatives table or section covers Mercado Pago (runner-up), Stripe, and PagBank with why not chosen. References the evaluation doc and T040 / CL #53. | `docs/adrs/0003-payment-provider.md` |
| EW-03 | `docs/commercial.md` Payments section no longer says provider not chosen; it names Asaas (and points at evaluation + ADR). Subprocessors baseline lists Asaas (or “Asaas (payments)”) instead of “Payment provider — TBD”. `docs/decision.md` payment gap no longer says the provider was not chosen; it records Asaas accepted and manual activation until T042. | `docs/commercial.md`, `docs/decision.md` |
| EW-04 | Only after EW-01–EW-03 and EW-05 hold: `ROADMAP-TASKS.md` checks T040; `COMMERCIAL-LAUNCH.md` checks item 53; this SDD status is `implemented`; `INDEX.md` T040 row is `implemented`. CL #54–#59 and #63 remain unchecked. T041–T043 remain unchecked. | those files |
| EW-05 | Diff does not add subscription state fields (T041), `POST /webhooks/payments`, payment webhook handlers, or any new/changed runtime payment code under `api/`, `domain/`, or `infrastructure/`. No T041/T042/T043 SDD bodies expanded beyond what T040 needs for cross-links. No changes to `requirements*.txt` or `docs/MVP_SCOPE.md`. | whole diff |
| EW-06 | `docs/specs/sdd/T040-builder-report.md` exists with one row per EW ID (`done` or `skipped`), files, and what changed, plus a **Files touched** list. This SDD includes **Builder report** and **Reviewer comparison** sections in T031 style. | SDD + builder report |

## Builder report

After implementation, write `docs/specs/sdd/T040-builder-report.md`:

| ID | Result (`done` or `skipped`) | Files | What changed |
|----|-------------------------------|-------|----------------|

Add a **Files touched** list of every path in the diff and the exact verification commands with results. The reviewer treats any path not justified by an ID as **extra**.

## Reviewer comparison

Read this file, the builder report, and the diff. Return only:

- One line per ID: `EW-xx match|gap — evidence`
- Extras: paths or behavior not in the table
- Bugs that break an ID or contradict the Asaas decision
- Verdict: accept or reject

Do not implement. Do not accept on “diff looks fine” alone if any EW row is unmet.

## Related

- [CONTEXT.md](../../../CONTEXT.md)
- [payments-evaluation.md](../../payments-evaluation.md)
- [ADR 0003](../../adrs/0003-payment-provider.md)
- [commercial.md](../../commercial.md)
- [COMMERCIAL-LAUNCH.md](../../COMMERCIAL-LAUNCH.md) Phase 6
- [decision.md](../../decision.md)
- [T042 SDD](./T042-payment-webhook-handler-sdd.md) (blocked until #53)

## Revision history

| Date | Change |
|------|--------|
| 2026-11-10 | Initial stub |
| 2026-11-15 | Orchestrator EW-01–EW-06 from parent decisions (Asaas, scored table, docs-only gate) |
