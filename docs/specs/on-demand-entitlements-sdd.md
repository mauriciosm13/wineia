# SDD — On-demand IA entitlements by `plan_tier` (T024)

**Status:** Implemented (MVP)  
**Depends on:** [customer-plan-tier.md](./customer-plan-tier.md) (T020), [commercial.md](../commercial.md)  
**Out of scope:** Webhook abuse / IP rate limits ([webhook-rate-limit.md](./webhook-rate-limit.md), T012); scheduled recommendation cadence ([entry-recommendation-cadence-sdd.md](./entry-recommendation-cadence-sdd.md), T021); global Claude budget stop (T061).

## Purpose

Gate **inbound WhatsApp IA** (`domain/services/messaging_service.py` via webhook) using persisted per-customer counters and tier limits. SUPERIOR subscribers get a higher daily on-demand cap than ENTRY (on-demand Gastón).

## Tier defaults (MVP — T060 may tune)

| `plan_tier` | Max on-demand IA replies / UTC day |
|-------------|-------------------------------------|
| `ENTRY` | 2 |
| `SUPERIOR` | 10 |

Constants live in `domain/on_demand_entitlements.py` (`ON_DEMAND_DAILY_LIMIT_BY_TIER`).

## Datastore fields (Customer)

| Field | Role |
|-------|------|
| `messages_sent_today` | Count of on-demand IA replies sent since last daily reset |
| `daily_reset` | ISO date (`YYYY-MM-DD`) of the UTC calendar day for the current counter |

Scheduled recommendation and weekly education jobs **do not** increment `messages_sent_today`.

## Daily reset (MVP)

**Read-path reset:** On each inbound message, if `daily_reset` ≠ today's UTC date, set `messages_sent_today` to `0` and update `daily_reset`.

**Future (M1 roadmap):** A scheduled job may reset counters at day boundary for all customers (batch). Read-path reset remains safe if the job is delayed or missing.

## Flow

1. Load customer (with `plan_tier` normalized to `ENTRY` when missing).
2. `reset_daily_counter_if_needed(customer, now)`.
3. `can_send_on_demand(customer, now)` — requires `status == active` and count &lt; tier limit.
4. On success: IA reply, increment `messages_sent_today`, persist `last_message_at`.

## Related

- [ROADMAP-TASKS.md](../ROADMAP-TASKS.md) — T024, T060  
- [COMMERCIAL-LAUNCH.md](../COMMERCIAL-LAUNCH.md) — #18a  
