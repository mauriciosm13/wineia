# PLAN — T051 Export/delete tooling

Source of truth: `CONTEXT.md` and Expected work EW-01–EW-07 in
`docs/specs/sdd/T051-export-delete-tooling-sdd.md`. On conflict, the SDD
Expected work table wins.

Branch: `feat/t051-export-delete-tooling` from `origin/main` (no `cursor/`
prefix).

`PLAN.md` is this handoff. It is not an Expected work product.

**Parallel:** Do not own T070. Payments T040–T043 parked. Skip T004.

## Order

| # | Task | EW | Depends on |
|---|------|----|------------|
| 1 | Pre-sale repo `get_by_whatsapp` + `delete` (abstract, Datastore, fake) | EW-01 | — |
| 2 | Domain `CustomerPrivacyService.export_customer` + tests | EW-02 | 1 |
| 3 | Domain `erase_customer` + tests | EW-03 | 1, 2 |
| 4 | Handler routes export/erase + route tests | EW-04 | 2, 3 |
| 5 | Ops runbook + PRODUCTION | EW-05 | 4 |
| 6 | Diff / coverage / lint gate | EW-07 | 1–5 |
| 7 | Status flips (T051, INDEX, CL #62) | EW-06 | 6 |
| 8 | Builder report | EW-01–EW-07 | 7 |

## Out of scope (do not do)

Payments T040–T043; T004; T070 ownership; hard-delete of recommendation
history / financial records; job-internal-secret on these paths; new pip deps.
