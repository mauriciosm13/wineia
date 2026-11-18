# SPEC — T050 Privacy/terms links at opt-in

**Status:** ready for implementation  
**Task:** T050 ([docs/ROADMAP-TASKS.md](docs/ROADMAP-TASKS.md))  
**Branch:** `feat/t050-privacy-terms-opt-in`  
**Binding sources:** [CONTEXT.md](CONTEXT.md), [PLAN.md](PLAN.md),
[docs/specs/sdd/T050-privacy-terms-opt-in-sdd.md](docs/specs/sdd/T050-privacy-terms-opt-in-sdd.md)
(Expected work EW-01–EW-08).

This file is the implementation contract. If it ever disagrees with the SDD
Expected work table, the SDD wins.

## Problem

Opt-in (pre-sale create / activation) does not show privacy/terms links or
persist consent metadata. CL #60 requires both.

## Goals

- Portuguese notice with privacy + terms links at pre-sale create and activation.
- Env URLs via `core/config` with placeholders when unset; never block registration.
- Persist `privacy_terms_version` + `privacy_terms_accepted_at` on opt-in.
- Domain owns rules; handlers thin; mark T050 + CL #60 when EW hold.

## Scope

| Slice | EW | Files |
|-------|----|-------|
| Config URL env + tests | EW-01 | `core/config.py`, core unit tests |
| Domain notice + consent helpers | EW-02 | `domain/privacy_terms.py`, domain tests |
| Pre-sale create consent + notice | EW-03 | pre-sale model/service + tests |
| Activate consent + notice | EW-04 | customer model, pre-sale service + tests |
| Thin handlers | EW-05 | pre-sale handler (verify) |
| Ops docs | EW-06 | DEPLOYMENT, PRODUCTION |
| Status flips | EW-07 | ROADMAP-TASKS T050, COMMERCIAL-LAUNCH #60, SDD, INDEX |
| Diff gate | EW-08 | whole diff |
| Builder report | EW-01–EW-08 | `docs/specs/sdd/T050-builder-report.md` |

## Out of scope

- T051 export/delete; T070/T071; payments; T004; legal PDF; new pip deps.

## Acceptance

All EW-01–EW-08 true; builder report written; reviewer judge accepts; pytest +
ruff + import style; domain/core coverage ≥ 95%.
