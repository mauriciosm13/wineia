# Micro-tasks — commercial & ops (WineAI)

Parent checklists: [COMMERCIAL-LAUNCH.md](./COMMERCIAL-LAUNCH.md) · product [ROADMAP.md](./ROADMAP.md)

**SDD (one per task):** [specs/sdd/INDEX.md](./specs/sdd/INDEX.md)

**Done in product roadmap (do not re-do):** M0 CI/CD, M1–M4 core APIs, M2 Twilio+signature, M3 Claude pipeline, partial M5 Tasks.

---

## Git & agents

- [x] T001 — `.cursor/rules/no-direct-main.mdc` — [SDD](./specs/sdd/T001-no-direct-main-sdd.md)
- [x] T002 — `CONTEXT.md` at repo root — [SDD](./specs/sdd/T002-context-handoff-sdd.md)
- [x] T003 — Operations docs under `docs/operations/` — [SDD](./specs/sdd/T003-operations-docs-sdd.md)
- [x] T004 — Branch protection on GitHub `main` (require PR + CI checks) — [SDD](./specs/sdd/T004-github-branch-protection-sdd.md) (runbook + Dependabot done; **Settings still human** — enable rule in GitHub UI)

## Security & jobs

- [x] T010 — Document `JOB_INTERNAL_SECRET` in DEPLOYMENT + implement middleware (→ CL #9) — [SDD](./specs/sdd/T010-job-internal-secret-sdd.md)
- [x] T011 — Secret Manager migration plan (→ CL #8) — [SDD](./specs/sdd/T011-secret-manager-migration-sdd.md)
- [x] T012 — Rate limit webhook (→ CL #10) — [SDD](./specs/sdd/T012-webhook-rate-limit-sdd.md)
- [x] T013 — `docs/threat-model.md` (→ CL #12) — [SDD](./specs/sdd/T013-threat-model-sdd.md)
- [x] T072 — Operator API auth via same `JOB_INTERNAL_SECRET` on `/customers*`, `/ia/suggestions`, `/recommendation-contents` (→ CL #19) — [SDD](./specs/sdd/T072-operator-api-auth-sdd.md)

## Tiers & cadence

- [x] T020 — Add `plan_tier` + `weekly_education_opt_in` to Customer (→ CL #17–18) — [SDD](./specs/sdd/T020-customer-plan-tier-sdd.md)
- [x] T021 — ENTRY cadence 2×/week enforcement (→ CL #20) — [SDD](./specs/sdd/T021-entry-recommendation-cadence-sdd.md) · [detail spec](./specs/entry-recommendation-cadence-sdd.md)
- [x] T022 — Weekly education job + opt-in filter (→ CL #25) — [SDD](./specs/sdd/T022-weekly-education-job-sdd.md)
- [x] T023 — One Claude call per broadcast slot + fan-out (→ CL #24) — [SDD](./specs/sdd/T023-recommendation-broadcast-slot-sdd.md) · [detail spec](./specs/recommendation-broadcast-slot.md)
- [x] T024 — **Domain + Datastore product entitlements:** tier-based on-demand limits (replace hardcoded `DAILY_LIMIT` in messaging), persisted counters, daily reset (M1). **Separate layer from T012** (webhook abuse / infra protection). Depends **T020**; extends **T060** for SUPERIOR caps. — [SDD](./specs/sdd/T024-on-demand-entitlements-sdd.md) · [detail spec](./specs/on-demand-entitlements-sdd.md)

## M5 completion

- [x] T030 — Implement `/workers/send-campaign` (→ ROADMAP M5) — [SDD](./specs/sdd/T030-send-campaign-worker-sdd.md)
- [x] T031 — Scheduler jobs in deploy/CD (→ ROADMAP M5) — [SDD](./specs/sdd/T031-scheduler-deploy-cd-sdd.md)
- [x] T032 — Full async webhook replies via queue (→ ROADMAP M2) — [SDD](./specs/sdd/T032-async-webhook-replies-sdd.md)

## Inbound media (WhatsApp)

Epic parent: [T074 SDD](./specs/sdd/T074-inbound-whatsapp-media-sdd.md) (→ ROADMAP M2, CL #16a). Do in order; each slice keeps text-only path working.

- [x] **T074** — Epic: inbound WhatsApp **image + audio** (no silent ignore) — umbrella SDD + research — [SDD](./specs/sdd/T074-inbound-whatsapp-media-sdd.md) (slices T075–T079 landed)
- [x] **T075** — Parse Twilio media fields (`NumMedia`, `MediaUrl0`, `MediaContentType0`); route media-only (empty `Body`) into domain instead of skipping — [SDD](./specs/sdd/T075-twilio-media-parser-sdd.md)
- [x] **T076** — Download media from `MediaUrl0` with Twilio HTTP Basic Auth (follow redirect); size/MIME guardrails — [SDD](./specs/sdd/T076-twilio-media-download-sdd.md)
- [x] **T077** — Audio → STT → existing text IA path (choose provider + ADR if new dep) — [SDD](./specs/sdd/T077-inbound-audio-stt-sdd.md)
- [x] **T078** — Image → multimodal Claude (+ optional `Body` caption); unsupported types get Portuguese reply — [SDD](./specs/sdd/T078-inbound-image-vision-sdd.md)
- [x] **T079** — Ops/docs + tests: PRODUCTION / WHATSAPP-COMPLIANCE / DATA-RETENTION notes; entitlements + Claude budget still apply; unit tests for media-only and failure copy — [SDD](./specs/sdd/T079-inbound-media-ops-tests-sdd.md)

## Payments — Asaas (unparked)

**Direction (2026-11-20):** prefer **Asaas** (contact started; no adesão/mensalidade; pay-on-success). Instagram → **direct Asaas checkout**; WineAI learns pay via **webhook**. Gate: finish **T040** ADR before implementing webhooks.

- [ ] T040 — Fill [payments-evaluation.md](./payments-evaluation.md) + ADR 0003 choose **Asaas** (→ CL #53) — [SDD](./specs/sdd/T040-payments-evaluation-adr-sdd.md)
- [ ] T041 — Subscription state fields on Customer (→ CL #54) — [SDD](./specs/sdd/T041-subscription-state-fields-sdd.md)
- [ ] T042 — Generic payment webhook contract (→ CL #56–57) — [SDD](./specs/sdd/T042-payment-webhook-handler-sdd.md)
- [ ] **T044** — **Asaas** webhook reception: `POST /webhooks/asaas`, auth, idempotency, map events → `plan_tier` / subscription status — [SDD](./specs/sdd/T044-asaas-payment-webhook-sdd.md)
- [ ] T043 — Manual provisioning runbook until webhooks stable (→ CL #55) — [SDD](./specs/sdd/T043-manual-provisioning-runbook-sdd.md)

## LGPD

- [x] T050 — Privacy/terms links at opt-in (→ CL #60) — [SDD](./specs/sdd/T050-privacy-terms-opt-in-sdd.md)
- [x] T051 — Export/delete tooling (→ CL #62) — [SDD](./specs/sdd/T051-export-delete-tooling-sdd.md)

## Superior tier caps

- [x] T060 — Per-user daily IA turn limit by tier (→ CL #28; **tier defaults in T024** — ops-tunable via `ON_DEMAND_DAILY_LIMIT_*` env) — [SDD](./specs/sdd/T060-per-tier-ia-caps-sdd.md)
- [x] T061 — Global Claude budget stop (→ CL #28) — [SDD](./specs/sdd/T061-global-claude-budget-stop-sdd.md)

## Ops hygiene

- [x] T070 — Refresh PRODUCTION.md after next route change — [SDD](./specs/sdd/T070-production-md-refresh-sdd.md)
- [x] T071 — Launch checklist doc (→ CL #68) — [SDD](./specs/sdd/T071-launch-checklist-doc-sdd.md) · [LAUNCH-CHECKLIST.md](./LAUNCH-CHECKLIST.md)
- [x] T073 — Launch compliance docs: WhatsApp/Twilio policy + LGPD retention + Claude budget ops note (→ CL #16, #61) — [SDD](./specs/sdd/T073-launch-compliance-docs-sdd.md)

## IA provider — xAI Grok (test / launch cost)

Epic parent: [T080 SDD](./specs/sdd/T080-grok-ia-stack-sdd.md) (→ ROADMAP M3, CL #29). Goal: **one vendor** for text + vision + STT (cheaper than Claude Sonnet + OpenAI Whisper in test volumes). Do after T075–T078 (media path exists); prefer landing T079 docs first or in parallel with T083.

- [x] **T080** — Epic: migrate on-demand + broadcast IA stack to **xAI Grok** (text/vision + STT); ADR superseding Whisper; cost assumptions — [SDD](./specs/sdd/T080-grok-ia-stack-sdd.md) (slices T081–T084 landed)
- [x] **T081** — ADR 0007: choose Grok for chat/vision + Grok Voice Transcribe for STT; mark ADR 0006 superseded — [SDD](./specs/sdd/T081-grok-provider-adr-sdd.md) · [ADR 0007](./adrs/0007-xai-grok-ia-stack.md)
- [x] **T082** — Grok chat + vision client (`requests` or thin HTTP); wire `ia_service` text + image paths; keep domain injectable; unit tests mocked — [SDD](./specs/sdd/T082-grok-chat-vision-client-sdd.md)
- [x] **T083** — Replace OpenAI Whisper with Grok STT (`POST /v1/stt`); drop `OPENAI_API_KEY` from runtime when unused — [SDD](./specs/sdd/T083-grok-stt-replace-whisper-sdd.md)
- [x] **T084** — Ops/docs: `XAI_API_KEY` in Secret Manager / DEPLOYMENT / PRODUCTION; `IA_DAILY_CALL_BUDGET` (+ legacy Claude alias); OpenAI not required — [SDD](./specs/sdd/T084-grok-ops-docs-sdd.md)

## Launch waitlist (pré-lista / discount links)

Epic: [T085 SDD](./specs/sdd/T085-launch-waitlist-sdd.md). Frontend form → public API; later ops send discounted Asaas checkout links. **Distinct from** operator `POST /customers/pre-sale`.

- [ ] **T085** — Epic: launch waitlist (phone WhatsApp, name, email, birth_date, created_at, updated_at; age gate) — [SDD](./specs/sdd/T085-launch-waitlist-sdd.md)
- [ ] **T086** — Domain model + Datastore `WaitlistLead` + age validation — [SDD](./specs/sdd/T086-waitlist-model-sdd.md)
- [ ] **T087** — Public `POST /waitlist` + rate limit + privacy notice — [SDD](./specs/sdd/T087-waitlist-public-post-sdd.md)
- [ ] **T088** — Operator list/export + runbook to send discount Asaas links — [SDD](./specs/sdd/T088-waitlist-operator-export-sdd.md)

**Summary:** **inbound media done**; **Grok stack T080–T084 done** (ops: set `XAI_API_KEY` on Cloud Run); **payments unparked (Asaas T040–T044)**; **waitlist T085–T088** for pré-lista + discount checkout links.
