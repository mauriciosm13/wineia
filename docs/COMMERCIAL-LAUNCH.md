# Commercial launch roadmap — WineAI

Complements milestone [ROADMAP.md](./ROADMAP.md) (M0–M7) with **go-to-market**, **security**, **cost**, and **LGPD** gates.

**Micro-tasks:** [ROADMAP-TASKS.md](./ROADMAP-TASKS.md)  
**Product tiers:** [commercial.md](./commercial.md)

Launch-ready when every `[ ]` here is `[x]` and **Definition of Done** below is true.

---

## Phase 1 — Engineering baseline

- [x] 1. Clean Architecture + tests + CI (pytest, ruff, coverage) — M0
- [x] 2. Docker CI + conventional commits — M0
- [x] 3. CD OIDC deploy (tag / dispatch) — M0, [DEPLOYMENT.md](./DEPLOYMENT.md)
- [x] 4. Git workflow documented — [GIT_WORKFLOW.md](./GIT_WORKFLOW.md)
- [x] 5. No direct commits to `main` (rule + PR workflow) — see `.cursor/rules/no-direct-main.mdc`
- [ ] 6. pip-audit or Dependabot in CI (optional hardening)

---

## Phase 2 — Security

- [x] 7. Twilio webhook signature validation — M2
- [x] 8. Secret Manager for Twilio, Claude, job secret (no long-lived keys in env files) — [SECRET-MANAGER-MIGRATION.md](./operations/SECRET-MANAGER-MIGRATION.md), ADR [0004](./adrs/0004-secret-manager-runtime-secrets.md)
- [x] 9. `JOB_INTERNAL_SECRET` on `/jobs/*` and `/workers/*`
- [x] 10. Rate limits on public endpoints where needed — [webhook-rate-limit.md](./specs/webhook-rate-limit.md) (`POST /webhook/whatsapp`)
- [ ] 11. IAM least privilege for Cloud Run SA
- [x] 12. Threat model doc (webhook abuse, LLM injection, forged jobs) — [threat-model.md](./threat-model.md)

---

## Phase 3 — Messaging and WhatsApp

- [x] 13. Twilio inbound/outbound — M2
- [x] 14. Daily cap + cancelar — M2 (evolve to **tier cadence** in Phase 5)
- [ ] 15. Async replies fully queue-based — M2 open item
- [ ] 16. Message templates / compliance doc for Twilio/WhatsApp policy

---

## Phase 4 — Tiers and catalog

- [x] 17. `plan_tier`: `ENTRY` | `SUPERIOR` (+ map existing `plan` field) — [customer-plan-tier.md](./specs/customer-plan-tier.md)
- [x] 18. `weekly_education_opt_in` on customer — [customer-plan-tier.md](./specs/customer-plan-tier.md)
- [x] 18a. **Domain + Datastore entitlements** per `plan_tier` (on-demand limits, persisted counters, daily reset) — separate from webhook abuse limits (Phase 2 #10 / T012); [on-demand-entitlements-sdd.md](./specs/on-demand-entitlements-sdd.md)
- [ ] 19. Admin/operator API to set tier and add-on
- [x] 20. Cadence: **2 recommendations / week** for ENTRY (replace daily-only semantics where wrong)

---

## Phase 5 — Cost-efficient AI and sends

- [x] 21. Claude sommelier + recommendation pipeline — M3
- [x] 22. Shared catalog rotation — M3
- [x] 23. Cloud Tasks enqueue on send-recommendations — M5 partial
- [x] 24. One Claude call per **broadcast slot**, fan-out same body — [recommendation-broadcast-slot.md](./specs/recommendation-broadcast-slot.md)
- [x] 25. Education weekly job + shared copy for opt-in cohort — [weekly-education-job.md](./specs/weekly-education-job.md)
- [ ] 26. `/workers/send-campaign` — M5
- [ ] 27. Scheduler in CD — M5
- [ ] 28. Superior tier: cap on-demand IA turns + daily budget

---

## Phase 6 — Billing

**Gate:** #53 before payment webhooks.

- [ ] 53. Choose payment API — [payments-evaluation.md](./payments-evaluation.md), [adrs/0003-payment-provider.md](./adrs/0003-payment-provider.md)
- [ ] 54. Subscription state model (`TRIAL`, `ACTIVE`, `PAST_DUE`, `CANCELED`)
- [ ] 55. Manual provisioning runbook (until #56)
- [ ] 56. Payment webhook → tier activation
- [ ] 57. Idempotent payment events
- [ ] 58. Pricing copy in [commercial.md](./commercial.md)
- [ ] 59. Expiry job when subscription ends

---

## Phase 7 — LGPD

- [ ] 60. Privacy policy + terms linked at opt-in
- [ ] 61. Data retention doc
- [ ] 62. Export / delete customer by phone
- [ ] 63. Subprocessors including payment provider after #53

---

## Phase 8 — Operations

- [x] 64. [operations/PRODUCTION.md](./operations/PRODUCTION.md) (as-is doc)
- [x] 65. [operations/INCIDENT-RESPONSE.md](./operations/INCIDENT-RESPONSE.md)
- [x] 66. [operations/OBSERVABILITY.md](./operations/OBSERVABILITY.md)
- [ ] 67. [CONTEXT.md](../CONTEXT.md) kept current each release
- [ ] 68. Launch checklist signed

---

## Definition of Done (commercial)

- Tiers and cadence match [commercial.md](./commercial.md); Portuguese user copy.
- Broadcast recommendations use **one IA generation per slot** where applicable.
- Payment provider chosen or explicit manual-only launch waiver documented.
- LGPD export/delete path exists.
- Ops runbooks accurate; on-call agent can diagnose prod from docs alone.
- All changes via PR to `main`; production deploy via tag/dispatch only.
