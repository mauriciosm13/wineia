# SPEC — T040 Payments evaluation + ADR 0003

**Status:** ready for implementation  
**Task:** T040 ([docs/ROADMAP-TASKS.md](docs/ROADMAP-TASKS.md))  
**Branch:** `feat/t040-payments-evaluation`  
**Binding sources:** [CONTEXT.md](CONTEXT.md), [PLAN.md](PLAN.md), [docs/specs/sdd/T040-payments-evaluation-adr-sdd.md](docs/specs/sdd/T040-payments-evaluation-adr-sdd.md) (Expected work EW-01–EW-06).

This file is the implementation contract. If it ever disagrees with the SDD Expected work table, the SDD wins.

## Problem

Payment provider undecided blocks CL #53 and T042 webhook design.

## Goals

- Scored evaluation (cost 40%, ease 35%, recurrence 25%) for four BR shortlist providers.
- ADR 0003 Accepted with Asaas; Mercado Pago runner-up.
- commercial.md + decision.md no longer TBD.
- CL #53 + T040 checked; SDD/INDEX implemented.
- Docs-only diff.

## Scope

| Slice | EW | Files |
|-------|----|-------|
| Evaluation | EW-01 | `docs/payments-evaluation.md` |
| ADR | EW-02 | `docs/adrs/0003-payment-provider.md` |
| Cross-docs | EW-03 | `docs/commercial.md`, `docs/decision.md` |
| Status flips | EW-04 | ROADMAP-TASKS, COMMERCIAL-LAUNCH #53, SDD, INDEX |
| Diff gate | EW-05 | whole diff |
| Builder report + SDD sections | EW-06 | SDD, `T040-builder-report.md` |

## Out of scope

- T041 fields; T042 webhook route/handler; T043 runbook body.
- Live sandbox calls; MDR contract signing.
- CL #63 checkbox; runtime Python payment code.
- New pip deps; `docs/MVP_SCOPE.md`; T004.

## Decision binding

| Item | Value |
|------|-------|
| Chosen provider | Asaas |
| Runner-up | Mercado Pago |
| Weights | cost 40%, ease 35%, recurrence 25% |
| Sandbox smoke | Ops prerequisite for T042, not T040 deliverable |

## Acceptance

Reviewer judges EW-01–EW-06 against builder report + diff. Accept only if every EW is **match**.
