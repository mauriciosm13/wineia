# PLAN — T050 Privacy/terms links at opt-in

Source of truth: `CONTEXT.md` and Expected work EW-01–EW-08 in
`docs/specs/sdd/T050-privacy-terms-opt-in-sdd.md`. On conflict, the SDD
Expected work table wins.

Branch: `feat/t050-privacy-terms-opt-in` from `origin/main` (no `cursor/`
prefix).

`PLAN.md` is this handoff. It is not an Expected work product.

**Parallel:** T071 may run elsewhere — do not touch CL #68 / T071 files.

## Order

| # | Task | EW | Depends on |
|---|------|----|------------|
| 1 | Config URL env + tests | EW-01 | — |
| 2 | Domain privacy_terms helpers + tests | EW-02 | — |
| 3 | Pre-sale model + create consent + notice | EW-03 | 1, 2 |
| 4 | Customer model + activate consent + notice | EW-04 | 2, 3 |
| 5 | Confirm handlers stay thin | EW-05 | 3, 4 |
| 6 | DEPLOYMENT / PRODUCTION light docs | EW-06 | 1 |
| 7 | Diff / coverage / lint gate | EW-08 | 1–6 |
| 8 | Status flips (T050, INDEX, CL #60) | EW-07 | 7 |
| 9 | Builder report | EW-01–EW-08 | 8 |

## Tasks

### 1. Config (EW-01)

Files: `core/config.py`, `tests/unit/core/test_config_and_queues.py`.

- `PRIVACY_POLICY_URL` / `TERMS_OF_SERVICE_URL` with placeholder defaults.

### 2. Domain helpers (EW-02)

- `domain/privacy_terms.py` + `tests/unit/domain/test_privacy_terms.py`.

### 3–4. Pre-sale create + activate (EW-03, EW-04)

- Stamp/copy consent; return `privacy_terms_notice`.
- Extend models; keep preference merge behavior.

### 5–9. Handlers, docs, gate, status, report

- Handlers pass-through only.
- DEPLOYMENT + PRODUCTION env notes.
- pytest, ruff, import style; domain/core coverage ≥ 95%.
- Flip T050 / SDD / INDEX; check CL #60 only.
- Write `docs/specs/sdd/T050-builder-report.md`.

## Out of scope (do not do)

Payments T040–T043; T004; T051; T070/T071; legal PDF; blocking
registration when URLs unset; new pip deps.
