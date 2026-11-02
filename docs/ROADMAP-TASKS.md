# Micro-tasks — commercial & ops (WineAI)

Parent checklists: [COMMERCIAL-LAUNCH.md](./COMMERCIAL-LAUNCH.md) · product [ROADMAP.md](./ROADMAP.md)

**Done in product roadmap (do not re-do):** M0 CI/CD, M1–M4 core APIs, M2 Twilio+signature, M3 Claude pipeline, partial M5 Tasks.

---

## Git & agents

- [x] T001 — `.cursor/rules/no-direct-main.mdc`
- [x] T002 — `CONTEXT.md` at repo root
- [x] T003 — Operations docs under `docs/operations/`
- [ ] T004 — Branch protection on GitHub `main` (require PR + CI checks)

## Security & jobs

- [x] T010 — Document `JOB_INTERNAL_SECRET` in DEPLOYMENT + implement middleware (→ CL #9)
- [x] T011 — Secret Manager migration plan (→ CL #8)
- [ ] T012 — Rate limit webhook (→ CL #10)
- [ ] T013 — `docs/threat-model.md` (→ CL #12)

## Tiers & cadence

- [ ] T020 — Add `plan_tier` + `weekly_education_opt_in` to Customer (→ CL #17–18)
- [ ] T021 — ENTRY cadence 2×/week enforcement (→ CL #20)
- [ ] T022 — Weekly education job + opt-in filter (→ CL #25)
- [ ] T023 — One Claude call per broadcast slot + fan-out (→ CL #24)

## M5 completion

- [ ] T030 — Implement `/workers/send-campaign` (→ ROADMAP M5)
- [ ] T031 — Scheduler jobs in deploy/CD (→ ROADMAP M5)
- [ ] T032 — Full async webhook replies via queue (→ ROADMAP M2)

## Payments (gate T040 first)

- [ ] T040 — Fill [payments-evaluation.md](./payments-evaluation.md) + ADR 0003 (→ CL #53)
- [ ] T041 — Subscription state fields (→ CL #54)
- [ ] T042 — Payment webhook handler (→ CL #56)
- [ ] T043 — Manual provisioning runbook (→ CL #55)

## LGPD

- [ ] T050 — Privacy/terms links at opt-in (→ CL #60)
- [ ] T051 — Export/delete tooling (→ CL #62)

## Superior tier caps

- [ ] T060 — Per-user daily IA turn limit (→ CL #28)
- [ ] T061 — Global Claude budget stop (→ CL #28)

## Ops hygiene

- [ ] T070 — Refresh PRODUCTION.md after next route change
- [ ] T071 — Launch checklist doc (→ CL #68)

**Summary:** 5 done · remainder open — expand tasks as you close CL items.
