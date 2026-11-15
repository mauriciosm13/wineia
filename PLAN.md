# PLAN — T060 Per-tier IA caps (ops-tunable)

Source of truth: `CONTEXT.md` and Expected work EW-01–EW-06 in
`docs/specs/sdd/T060-per-tier-ia-caps-sdd.md`. On conflict, the SDD Expected
work table wins.

Branch: `feat/t060-per-tier-ia-caps` from `origin/main` (no `cursor/` prefix).

`PLAN.md` is this handoff. It is not an Expected work product.

## Order

| # | Task | EW | Depends on |
|---|------|----|------------|
| 1 | Config: env-backed ENTRY/SUPERIOR limits + parse rules | EW-01 | — |
| 2 | Domain: consume `core.config`; tests for default + override | EW-02, EW-03 | 1 |
| 3 | Ops / decision / entitlements detail docs | EW-04 | 2 |
| 4 | Diff and coverage gate | EW-06 | 1–3 |
| 5 | Status flips (T060, INDEX, CL #28 wording) | EW-05 | 4 |
| 6 | Builder report | EW-01–EW-06 | 5 |

## Tasks

### 1. Config (EW-01)

Files: `core/config.py`, `tests/unit/core/test_config_and_queues.py`.

- Add `ON_DEMAND_DAILY_LIMIT_ENTRY` / `ON_DEMAND_DAILY_LIMIT_SUPERIOR`.
- Defaults 2 / 10; invalid → default; `0` allowed.
- Tests via `importlib.reload` + monkeypatch.

### 2. Domain entitlements (EW-02, EW-03)

Files: `domain/on_demand_entitlements.py`,
`tests/unit/domain/test_on_demand_entitlements.py`.

- Read limits from `core.config` at call time.
- Tests: defaults, env overrides affecting `can_send_on_demand`, reset /
  inactive / unknown tier preserved.

### 3. Docs (EW-04)

- `DEPLOYMENT.md` env table; `PRODUCTION.md` note; `decision.md` bullet;
  `on-demand-entitlements-sdd.md` env path.

### 4–6. Gate, status, report

- pytest, ruff, import style; domain/core coverage ≥ 95%.
- Flip T060 / SDD / INDEX; clarify CL #28 (caps vs T061 budget).
- Write `docs/specs/sdd/T060-builder-report.md`.

## Out of scope (do not do)

T061; T012 algorithms; T021; payments T040–T043; T004; T050/T051; root
`config.py` rewrite; per-customer Datastore cap overrides.
