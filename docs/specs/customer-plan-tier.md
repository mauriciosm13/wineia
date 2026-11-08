# Spec — Customer `plan_tier` and education opt-in

**Status:** implemented (T020 / COMMERCIAL-LAUNCH #17–18)  
**Scope:** Customer model, Datastore kind `Customer`, HTTP `/customers` API

## Fields

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `plan_tier` | `ENTRY` \| `SUPERIOR` | `ENTRY` | Commercial tier code — see [commercial.md](../commercial.md) |
| `weekly_education_opt_in` | boolean | `false` | Weekly didactic message add-on |
| `plan` | string (optional) | — | **Legacy** operator label (e.g. `free`, `premium`); not used for entitlement logic |

There is **no** automatic mapping from legacy `plan` strings to `plan_tier`. Operators set `plan_tier` explicitly via create or PATCH until billing integration (T041+).

## Migration-on-read

Datastore entities without `plan_tier` or `weekly_education_opt_in` are normalized in `CustomerService` on every read:

- Missing `plan_tier` → `ENTRY`
- Missing / null opt-in → `false`

Writes persist the full dict including new fields when customers are created or updated.

## API

**POST `/customers`** — optional body keys: `plan_tier`, `weekly_education_opt_in`.

**PATCH `/customers/{phone}`** — updatable: `plan_tier`, `weekly_education_opt_in` (plus existing fields).

**GET** list/single — always includes both fields after normalization.

Validation errors → `400` with `{"error": "..."}`.

## Related

- [commercial.md](../commercial.md) — tier promises
- [weekly-education-job.md](./weekly-education-job.md) — T022 job
- [on-demand-entitlements-sdd.md](./on-demand-entitlements-sdd.md) — T024 on-demand daily caps
- [ROADMAP-TASKS.md](../ROADMAP-TASKS.md) — T021 cadence, T024 entitlements
