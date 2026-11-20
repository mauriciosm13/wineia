# SDD — HMAC per-request operator auth (T089)

**Status:** draft  
**Task:** [T089](../../ROADMAP-TASKS.md)  
**Depends on:** T010, T072 (shared secret baseline)  
**Related:** [threat-model.md](../../threat-model.md) §4.2 / §4.5 residual risk (long-lived header secret)

## Problem

Operator and job callers today send a **static** header `X-Job-Internal-Secret` equal to `JOB_INTERNAL_SECRET`. If the secret leaks (logs, Postman history, compromised laptop), an attacker can replay it on any gated path until rotation. Twilio already uses **per-request HMAC**; operator APIs do not.

## Goals

1. Accept a **signed request** for operator surfaces (`/customers*`, `/ia/suggestions`, `/recommendation-contents`, `GET /waitlist`) using HMAC over method + path + body + timestamp (exact canonical string decided in Expected work when implemented).
2. Reject stale timestamps (anti-replay window, e.g. ±5 minutes).
3. Keep **fail closed** if signing key unset.
4. Document Postman/curl signing recipe; rotate via Secret Manager.
5. During transition, allow either static header **or** HMAC (feature flag / dual-accept), then deprecate static header for human/ops callers.

## Non-goals (this task)

- Replacing Cloud Scheduler / Cloud Tasks auth with OIDC (separate follow-up; preferred for GCP-internal callers).
- Changing Twilio webhook signature.
- Public `POST /waitlist` / `/health`.
- Payments (T040–T044).

## Sketch (normative direction; lock in EW table at implement time)

| Item | Direction |
|------|-----------|
| Key material | Reuse or sibling of `JOB_INTERNAL_SECRET` in Secret Manager |
| Headers | e.g. `X-WineAI-Timestamp`, `X-WineAI-Signature` (HMAC-SHA256 hex/base64) |
| Canonical string | `METHOD\nPATH\nTIMESTAMP\nSHA256(body)` (TBD in EW) |
| Clock skew | Configurable max age (default 300s) |
| Jobs/workers | May keep static header short-term **or** switch to OIDC in a later task |

## Acceptance criteria (epic-level)

- [ ] SDD expanded with Expected work EW-xx + builder report + reviewer judge
- [ ] Dual-accept or cutover documented in DEPLOYMENT / PRODUCTION
- [ ] Unit tests: valid sig, bad sig, expired timestamp, missing headers
- [ ] Threat model updated (residual risk reduced for operator replay)

## Revision history

| Date | Change |
|------|--------|
| 2026-11-20 | Draft from product ask (HMAC vs fixed secret) |
