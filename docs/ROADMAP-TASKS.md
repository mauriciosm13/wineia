# Micro-tasks — commercial & ops (WineAI)

Parent checklists: [COMMERCIAL-LAUNCH.md](./COMMERCIAL-LAUNCH.md) · product [ROADMAP.md](./ROADMAP.md)

**SDD (one per task):** [specs/sdd/INDEX.md](./specs/sdd/INDEX.md)

**Done in product roadmap (do not re-do):** M0 CI/CD, M1–M4 core APIs, M2 Twilio+signature, M3 Claude pipeline, partial M5 Tasks.

---

## Git & agents

- [x] T001 — `.cursor/rules/no-direct-main.mdc` — [SDD](./specs/sdd/T001-no-direct-main-sdd.md)
- [x] T002 — `CONTEXT.md` at repo root — [SDD](./specs/sdd/T002-context-handoff-sdd.md)
- [x] T003 — Operations docs under `docs/operations/` — [SDD](./specs/sdd/T003-operations-docs-sdd.md)
- [ ] T004 — Branch protection on GitHub `main` (require PR + CI checks) — [SDD](./specs/sdd/T004-github-branch-protection-sdd.md)

## Security & jobs

- [x] T010 — Document `JOB_INTERNAL_SECRET` in DEPLOYMENT + implement middleware (→ CL #9) — [SDD](./specs/sdd/T010-job-internal-secret-sdd.md)
- [x] T011 — Secret Manager migration plan (→ CL #8) — [SDD](./specs/sdd/T011-secret-manager-migration-sdd.md)
- [x] T012 — Rate limit webhook (→ CL #10) — [SDD](./specs/sdd/T012-webhook-rate-limit-sdd.md)
- [x] T013 — `docs/threat-model.md` (→ CL #12) — [SDD](./specs/sdd/T013-threat-model-sdd.md)

## Tiers & cadence

- [x] T020 — Add `plan_tier` + `weekly_education_opt_in` to Customer (→ CL #17–18) — [SDD](./specs/sdd/T020-customer-plan-tier-sdd.md)
- [x] T021 — ENTRY cadence 2×/week enforcement (→ CL #20) — [SDD](./specs/sdd/T021-entry-recommendation-cadence-sdd.md) · [detail spec](./specs/entry-recommendation-cadence-sdd.md)
- [x] T022 — Weekly education job + opt-in filter (→ CL #25) — [SDD](./specs/sdd/T022-weekly-education-job-sdd.md)
- [x] T023 — One Claude call per broadcast slot + fan-out (→ CL #24) — [SDD](./specs/sdd/T023-recommendation-broadcast-slot-sdd.md) · [detail spec](./specs/recommendation-broadcast-slot.md)
- [x] T024 — **Domain + Datastore product entitlements:** tier-based on-demand limits (replace hardcoded `DAILY_LIMIT` in messaging), persisted counters, daily reset (M1). **Separate layer from T012** (webhook abuse / infra protection). Depends **T020**; extends **T060** for SUPERIOR caps. — [SDD](./specs/sdd/T024-on-demand-entitlements-sdd.md) · [detail spec](./specs/on-demand-entitlements-sdd.md)

## M5 completion

- [ ] T030 — Implement `/workers/send-campaign` (→ ROADMAP M5) — [SDD](./specs/sdd/T030-send-campaign-worker-sdd.md)
- [ ] T031 — Scheduler jobs in deploy/CD (→ ROADMAP M5) — [SDD](./specs/sdd/T031-scheduler-deploy-cd-sdd.md)
- [ ] T032 — Full async webhook replies via queue (→ ROADMAP M2) — [SDD](./specs/sdd/T032-async-webhook-replies-sdd.md)

## Payments (gate T040 first)

- [ ] T040 — Fill [payments-evaluation.md](./payments-evaluation.md) + ADR 0003 (→ CL #53) — [SDD](./specs/sdd/T040-payments-evaluation-adr-sdd.md)
- [ ] T041 — Subscription state fields (→ CL #54) — [SDD](./specs/sdd/T041-subscription-state-fields-sdd.md)
- [ ] T042 — Payment webhook handler (→ CL #56) — [SDD](./specs/sdd/T042-payment-webhook-handler-sdd.md)
- [ ] T043 — Manual provisioning runbook (→ CL #55) — [SDD](./specs/sdd/T043-manual-provisioning-runbook-sdd.md)

## LGPD

- [ ] T050 — Privacy/terms links at opt-in (→ CL #60) — [SDD](./specs/sdd/T050-privacy-terms-opt-in-sdd.md)
- [ ] T051 — Export/delete tooling (→ CL #62) — [SDD](./specs/sdd/T051-export-delete-tooling-sdd.md)

## Superior tier caps

- [ ] T060 — Per-user daily IA turn limit by tier (→ CL #28; **tier defaults in T024** — ops tuning / config follow-up) — [SDD](./specs/sdd/T060-per-tier-ia-caps-sdd.md)
- [ ] T061 — Global Claude budget stop (→ CL #28) — [SDD](./specs/sdd/T061-global-claude-budget-stop-sdd.md)

## Ops hygiene

- [ ] T070 — Refresh PRODUCTION.md after next route change — [SDD](./specs/sdd/T070-production-md-refresh-sdd.md)
- [ ] T071 — Launch checklist doc (→ CL #68) — [SDD](./specs/sdd/T071-launch-checklist-doc-sdd.md)

**Summary:** 10 done · remainder open — expand tasks as you close CL items.
