# Builder report — T040 Payments evaluation + ADR 0003

**SDD:** [T040-payments-evaluation-adr-sdd.md](./T040-payments-evaluation-adr-sdd.md)  
**Branch:** `feat/t040-payments-evaluation`  
**Date:** 2026-11-15

## Expected work

| ID | Result | Files | What changed |
|----|--------|-------|--------------|
| EW-01 | done | `docs/payments-evaluation.md` | Status **Asaas chosen**; runner-up Mercado Pago. Requirements table kept (recurring, webhooks+idempotency, Pix+card, sandbox). Scoring method documents weights cost 40% / ease 35% / recurrence 25%. Scored table for Mercado Pago, Stripe, Asaas, PagBank with 1–10 scores and weighted totals (Asaas 8.50 first). Prose justifies CNPJ, Pix+card, recurrence, webhooks/idempotency, sandbox. MDR/fees need ops verification; sandbox subscription+webhook smoke documented as **ops prerequisite for T042**, not a T040 deliverable. |
| EW-02 | done | `docs/adrs/0003-payment-provider.md` | Status **Accepted** (2026-11-15). Decision: Asaas; Mercado Pago runner-up; no webhook code in T040; manual until T042; sandbox smoke = T042 ops prereq. Consequences: webhook shape deferred to T042; subprocessors; LGPD DPA; manual provisioning. Alternatives: Mercado Pago, Stripe, PagBank, manual-only. Related T040 / CL #53 / evaluation. |
| EW-03 | done | `docs/commercial.md`, `docs/decision.md` | Payments section names Asaas + ADR/evaluation links; subprocessors lists `Asaas (payments)` instead of TBD. decision.md product bullet records Asaas Accepted and manual until T042. |
| EW-04 | done | `docs/ROADMAP-TASKS.md`, `docs/COMMERCIAL-LAUNCH.md`, `docs/specs/sdd/T040-payments-evaluation-adr-sdd.md`, `docs/specs/sdd/INDEX.md` | Flipped only after EW-01–EW-03 and EW-05: T040 checked, #53 checked (Asaas), SDD status `implemented`, INDEX `implemented`. #54–#59 and #63 unchecked; T041–T043 unchecked. |
| EW-05 | done | whole diff | `git diff --name-only` has no `api/`, `domain/`, or `infrastructure/` paths; no `/webhooks/payments`; no T041 field work; no `requirements*.txt` or `docs/MVP_SCOPE.md`. Docs/decision only. |
| EW-06 | done | SDD, this file | SDD expanded with Problem, Goals, Non-goals, Behavior, Expected work, Builder report, Reviewer comparison. This report has one row per EW + Files touched. |

## Deviations from the SDD / SPEC

None.

## Files touched

Handoff files (CONTEXT / PLAN / SPEC): not Expected work products; listed for the reviewer.

| Path | EW |
|------|----|
| `CONTEXT.md` | handoff |
| `PLAN.md` | handoff |
| `SPEC.md` | handoff |
| `docs/payments-evaluation.md` | EW-01 |
| `docs/adrs/0003-payment-provider.md` | EW-02 |
| `docs/commercial.md` | EW-03 |
| `docs/decision.md` | EW-03 |
| `docs/ROADMAP-TASKS.md` | EW-04 |
| `docs/COMMERCIAL-LAUNCH.md` | EW-04 |
| `docs/specs/sdd/T040-payments-evaluation-adr-sdd.md` | EW-04 (status) + EW-06 (structure) |
| `docs/specs/sdd/INDEX.md` | EW-04 |
| `docs/specs/sdd/T040-builder-report.md` (new) | EW-06 |

Untracked and **not** part of this change: `docs/design/`, `frontend/`.

## Verification commands and results

| Command | Result |
|---------|--------|
| `git diff --name-only origin/main` (expected deliverables) | Only CONTEXT, PLAN, SPEC, and the docs paths above — no runtime payment code |
| Grep `docs/payments-evaluation.md` for weights `40%` / `35%` / `25%` and providers | Present; Asaas weighted 8.50 |
| Grep ADR for `Accepted` and `Asaas` | Present |
| Grep commercial/decision for TBD payment provider | Payments/subprocessors TBD removed; Asaas named |
| Grep CL #53 and T040 checkboxes | Both `[x]` |
| Grep INDEX T040 | `implemented` |
| Confirm CL #54–#59, #63 and T041–T043 still `[ ]` | Yes |
