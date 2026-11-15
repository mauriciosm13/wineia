# PLAN — T040 Payments evaluation + ADR 0003

Source of truth: `CONTEXT.md` and Expected work EW-01–EW-06 in `docs/specs/sdd/T040-payments-evaluation-adr-sdd.md`. On conflict, the SDD Expected work table wins.

Branch: `feat/t040-payments-evaluation` from `origin/main`.

`PLAN.md` is this handoff. It is not an Expected work product.

## Order

| # | Task | EW | Depends on |
|---|------|----|------------|
| 1 | Expand SDD (Problem, Goals, Non-goals, Behavior, EW table, Builder/Reviewer sections) | EW-06 (structure) | — |
| 2 | Complete scored `payments-evaluation.md` | EW-01 | 1 |
| 3 | Accept ADR 0003 (Asaas) | EW-02 | 2 |
| 4 | Update `commercial.md` + `decision.md` | EW-03 | 3 |
| 5 | Diff gate (docs-only / no runtime payment code) | EW-05 | 2–4 |
| 6 | Status flips (T040, CL #53, SDD, INDEX) | EW-04 | 5 |
| 7 | Builder report | EW-06 | 6 |

## Tasks

### 1. SDD expansion (EW-06 structure)

File: `docs/specs/sdd/T040-payments-evaluation-adr-sdd.md`.

- Match T031 shape: Problem, Goals, Non-goals, Behavior, Expected work, Builder report, Reviewer comparison.
- Non-goals: no T041/T042/T043 code; sandbox smoke = T042 ops prereq.

### 2. Evaluation (EW-01)

File: `docs/payments-evaluation.md`.

- Scored table: Mercado Pago, Stripe, Asaas, PagBank; weights cost 40% / ease 35% / recurrence 25%.
- Prose: CNPJ, Pix+card, recurrence, webhooks/idempotency, sandbox.
- Winner Asaas; runner-up Mercado Pago; MDR disclaimer; T042 sandbox ops gate.

### 3. ADR (EW-02)

File: `docs/adrs/0003-payment-provider.md`.

- Status Accepted; decision Asaas; consequences; alternatives.

### 4. Cross-docs (EW-03)

Files: `docs/commercial.md`, `docs/decision.md`.

- Remove TBD for payment provider; name Asaas.

### 5. Gate + flips (EW-05, EW-04)

- Confirm no runtime payment code in the diff.
- Check T040 and CL #53; SDD + INDEX `implemented`.

### 6. Builder report (EW-06)

File: `docs/specs/sdd/T040-builder-report.md`.

## Out of scope

See CONTEXT.md and SDD Non-goals.
