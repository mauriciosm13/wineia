# Data retention (LGPD)

Operator notes for commercial launch item **#61** (task **T073**). Spec: [T073-launch-compliance-docs-sdd.md](../specs/sdd/T073-launch-compliance-docs-sdd.md).

This is the retention **intent** for MVP launch. It is not a substitute for legal review of the public privacy policy.

## What we store (PII inventory)

### Customer (Datastore, phone key)

| Field | Notes |
|-------|-------|
| `phone` | Primary key / WhatsApp identity |
| `name` | Display name |
| `status` | Lifecycle (`active`, `canceled`, …) |
| `plan` / `plan_tier` | Commercial tier (`ENTRY` \| `SUPERIOR`) |
| `preferences` | String list (taste / profile signals) |
| `weekly_education_opt_in` | Education cohort flag |
| `privacy_terms_version` / `privacy_terms_accepted_at` | Consent metadata (T050) |
| Operational counters / cadence fields | e.g. on-demand IA counters, recommendation window counters — not display PII, retained for product limits |

### PreSaleCustomer (Datastore, email key)

| Field | Notes |
|-------|-------|
| `email` | Lead key |
| `name`, `whatsapp` | Lead identity |
| `preferences` | Optional profile signals |
| `privacy_terms_version` / `privacy_terms_accepted_at` | Consent at create/activate (T050) |

### Not stored in product today

- Payment instruments, card PANs, or billing provider customer IDs (payments parked — T040–T043 / CL #53+).
- Application passwords or API secrets inside customer entities.

## Retention intent

| Data | Intent |
|------|--------|
| Active Customer / PreSale lead | Retain while the commercial relationship (or lead process) is live. |
| After customer cancel / erase request | Operator **anonymize** via T051 erase: name/preferences/consent cleared; status `canceled`; phone key kept; linked pre-sale **deleted**. See [LGPD-EXPORT-DELETE.md](./LGPD-EXPORT-DELETE.md). |
| Recommendation / message history | **Not** hard-deleted by T051. Retain until a stronger retention schedule or legal hold says otherwise. |
| Claude / Twilio logs | Subject to those vendors’ retention; avoid putting secrets in prompts or customer records. |
| Payment / financial records | None in product yet. When payments land, define retention with CL #63 (subprocessors) and do not hard-delete without policy. |

Default posture for launch: **minimize** new PII fields; prefer erase/anonymize over silent indefinite display of personal data after a delete request.

## Export and erase (rights tooling)

| Need | Mechanism |
|------|-----------|
| Consent at opt-in | T050 — privacy/terms notice + persisted consent fields on pre-sale create/activate |
| Export by phone | `GET /customers/{phone}/export` — [LGPD-EXPORT-DELETE.md](./LGPD-EXPORT-DELETE.md), [T051 SDD](../specs/sdd/T051-export-delete-tooling-sdd.md) |
| Erase / anonymize by phone | `POST /customers/{phone}/erase` — same runbook |

Export/erase routes share the unauthenticated `/customers*` operator surface — treat as internal-only.

## Subprocessors and processors (MVP)

| Party | Role | Data involved |
|-------|------|----------------|
| **Google Cloud** (Cloud Run, Datastore, Cloud Tasks, Scheduler, Secret Manager) | Primary infrastructure / processor | Customer and lead records, job payloads, secrets references |
| **Twilio** | WhatsApp delivery subprocessor | Phone numbers and message bodies |
| **Anthropic (Claude)** | Generation subprocessor | Prompt context derived from user messages / catalog copy (no payment data) |

Payment provider subprocessors are **deferred** until CL #53 / #63 after a provider is chosen.

## Operator checklist

- [ ] Public privacy policy describes the inventory and retention intent above (or a reviewed equivalent).
- [ ] Production `PRIVACY_POLICY_URL` / `TERMS_OF_SERVICE_URL` are live pages.
- [ ] Operators know how to run export/erase ([LGPD-EXPORT-DELETE.md](./LGPD-EXPORT-DELETE.md)).
- [ ] No payment PANs or provider secrets are written into Datastore customer rows.

## Related

- [LGPD-EXPORT-DELETE.md](./LGPD-EXPORT-DELETE.md)
- [WHATSAPP-COMPLIANCE.md](./WHATSAPP-COMPLIANCE.md)
- [PRODUCTION.md](./PRODUCTION.md)
- [COMMERCIAL-LAUNCH.md](../COMMERCIAL-LAUNCH.md) item 61
- [T050 privacy/terms opt-in](../specs/sdd/T050-privacy-terms-opt-in-sdd.md)
- [T051 export/delete tooling](../specs/sdd/T051-export-delete-tooling-sdd.md)
