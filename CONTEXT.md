# CONTEXT — WineAI (wineia)

> Read first. Product milestones: [`docs/ROADMAP.md`](docs/ROADMAP.md). Commercial launch checklist: [`docs/COMMERCIAL-LAUNCH.md`](docs/COMMERCIAL-LAUNCH.md). Micro-tasks: [`docs/ROADMAP-TASKS.md`](docs/ROADMAP-TASKS.md).

## Primary objective (current)

**T040** — Complete the Brazil payment-provider evaluation and accept **ADR 0003** with **Asaas** as the chosen provider. Docs and decision only. This is the COMMERCIAL-LAUNCH **#53** gate before T042 payment webhooks.

The comparison contract is [`docs/specs/sdd/T040-payments-evaluation-adr-sdd.md`](docs/specs/sdd/T040-payments-evaluation-adr-sdd.md). Its **Expected work** list (EW-01…) is what the reviewer checks against the builder report. Do not add behavior that list does not name. On conflict, the SDD Expected work table wins over PLAN.md / SPEC.md.

Skip **T004** (GitHub admin).

## Decisions already made (parent defaults, 2026-11-15)

| Topic | Decision |
|-------|----------|
| Scope | **Docs/decision only.** No payment webhook code, no new routes, no T041/T042/T043 implementation. |
| Evaluation | Complete `payments-evaluation.md` with a scored table: weights **cost 40%**, **ease 35%**, **recurrence 25%**. Shortlist: Mercado Pago, Stripe, Asaas, PagBank. Justify scores in prose (CNPJ, Pix+card, recurring billing, webhooks/idempotency, sandbox). Note live MDR/fees need ops verification before production cutover. |
| Provider | **Asaas** chosen (recurrence-first BR SaaS + Pix + card + webhooks). **Runner-up: Mercado Pago.** |
| ADR 0003 | Status **Accepted**. Record consequences: webhook shape deferred to T042; subprocessors update; LGPD DPA; manual provisioning until T042. |
| Sandbox smoke | Subscription + webhook sandbox smoke is an **ops prerequisite for T042**, not a T040 code deliverable. Document in evaluation + ADR + SDD non-goals. |
| Status flips | Mark COMMERCIAL-LAUNCH #53 and ROADMAP-TASKS T040 when EW hold; SDD + INDEX → `implemented`. |
| Cross-docs | `docs/commercial.md` subprocessors and Payments section, and `docs/decision.md` payment gap, must no longer say provider TBD. |
| Language | English for code/docs/commits; Conventional Commits; never push `main`. |

## Decisions made by the orchestrator

| Topic | Decision |
|-------|----------|
| EW IDs | EW-01 evaluation table; EW-02 ADR Accepted; EW-03 commercial + decision no TBD; EW-04 status flips; EW-05 non-goals / no runtime code; EW-06 builder report + reviewer sections. |
| Score scale | 1–10 per criterion; weighted total = cost×0.40 + ease×0.35 + recurrence×0.25. Asaas ranks first; Mercado Pago second. |
| CL #63 | Do **not** check #63 (LGPD subprocessors checklist item). Naming Asaas in `commercial.md` is enough for T040; #63 stays for Phase 7. |
| ROADMAP.md | Flip payment-provider / #53 wording only if it still says undecided; do not invent a new milestone. |
| Branch | `feat/t040-payments-evaluation` from `origin/main`. No `cursor/` prefix, no `-afd2` / `-79b7` suffix. |

## Out of scope

- T041 subscription state fields in Datastore/API.
- T042 `POST /webhooks/payments` or any payment webhook handler.
- T043 manual provisioning runbook body (beyond noting manual until T042).
- Runtime Python under `api/`, `domain/`, or `infrastructure/` for payments.
- New pip dependencies; `docs/MVP_SCOPE.md`.
- Live sandbox API calls or fee scraping in this task.
- T004 GitHub branch protection.

## Relevant files

| File | Role |
|------|------|
| `docs/specs/sdd/T040-payments-evaluation-adr-sdd.md` | Expanded SDD + Expected work (judge contract) |
| `docs/specs/sdd/T040-builder-report.md` | Builder report (one row per EW) |
| `docs/payments-evaluation.md` | Scored comparison + requirements coverage |
| `docs/adrs/0003-payment-provider.md` | ADR Accepted — Asaas |
| `docs/commercial.md` | Payments + subprocessors name Asaas |
| `docs/decision.md` | Payment gap no longer “not chosen” |
| `docs/COMMERCIAL-LAUNCH.md` | Check #53 |
| `docs/ROADMAP-TASKS.md` | Check T040 |
| `docs/specs/sdd/INDEX.md` | T040 → implemented |
| `PLAN.md`, `SPEC.md` | Handoff (not EW products) |

## Acceptance criteria

See EW-01… in the SDD. In short:

- [ ] Scored evaluation table with stated weights; prose covers CNPJ, Pix+card, recurrence, webhooks/idempotency, sandbox; MDR disclaimer; sandbox smoke = T042 ops prereq.
- [ ] ADR 0003 Accepted: Asaas; Mercado Pago runner-up; consequences recorded.
- [ ] `commercial.md` and `decision.md` no longer TBD for provider.
- [ ] CL #53 + T040 checked; SDD/INDEX `implemented`.
- [ ] Diff has no T041 fields, no `/webhooks/payments`, no payment runtime code.
- [ ] Builder report present; reviewer returns match/gap per EW and accept/reject.

## Git policy (fixed)

Branch: `feat/t040-payments-evaluation` from `origin/main` (no `cursor/` prefix — see [`docs/GIT_WORKFLOW.md`](docs/GIT_WORKFLOW.md)). **Never push to `main`.** Conventional Commits, English, lowercase subject. Parent creates the GitHub PR; leave PR URL unset if ManagePullRequest is parent-owned. Commit bodies wrap at 72 characters (commitlint `body-max-line-length` is 100).

## Agent handoff

On-call: [`.cursor/agents/on-call.md`](.cursor/agents/on-call.md).

Builder report path: `docs/specs/sdd/T040-builder-report.md` (one row per Expected work ID, files, done or skipped, plus Files touched). The reviewer reads that file, the SDD, and the diff, and is the judge. The reviewer does not edit any file.
