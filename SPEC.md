# SPEC — T051 Export/delete tooling

**Status:** ready for implementation  
**Task:** T051 ([docs/ROADMAP-TASKS.md](docs/ROADMAP-TASKS.md))  
**Branch:** `feat/t051-export-delete-tooling`  
**Binding sources:** [CONTEXT.md](CONTEXT.md), [PLAN.md](PLAN.md),
[docs/specs/sdd/T051-export-delete-tooling-sdd.md](docs/specs/sdd/T051-export-delete-tooling-sdd.md)
(Expected work EW-01–EW-07).

This file is the implementation contract. If it ever disagrees with the SDD
Expected work table, the SDD wins.

## Problem

No operator path to export or anonymize a customer by phone for LGPD (CL #62).

## Goals

- `GET /customers/{phone}/export` → JSON PII dump (no secrets).
- `POST /customers/{phone}/erase` → anonymize customer + delete linked pre-sale.
- Domain owns rules; handlers thin; ops runbook + PRODUCTION docs.
- Mark T051 + CL #62 when EW hold.

## Scope

| Slice | EW | Files |
|-------|----|-------|
| Pre-sale repo methods | EW-01 | abstract + Datastore + fake |
| Export service | EW-02 | `customer_privacy_service.py` + tests |
| Erase service | EW-03 | same |
| HTTP routes | EW-04 | `customer_handler.py` + route tests |
| Ops docs | EW-05 | `LGPD-EXPORT-DELETE.md`, `PRODUCTION.md` |
| Status flips | EW-06 | ROADMAP-TASKS T051, CL #62, SDD, INDEX |
| Diff gate | EW-07 | whole diff |
| Builder report | EW-01–EW-07 | `docs/specs/sdd/T051-builder-report.md` |

## Out of scope

Payments; T004; T070 ownership; hard-delete of history/financial; app auth on
these paths; new pip deps.
