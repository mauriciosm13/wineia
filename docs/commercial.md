# Commercial model — WineAI

**Audience:** product owner, operators, agents planning billing and tiers.

Internal marketing names for tiers are **TBD**. Use stable codes in Datastore/API.

## Tiers

| Code | Customer promise | Cost driver |
|------|------------------|-------------|
| `ENTRY` | **2 recommendation messages / week** (scheduled) | 1× Claude call per slot + N Twilio sends |
| `SUPERIOR` | Entry + **on-demand Gastón** in inbound chat | Per-conversation Claude (cap per user/day) |
| Education add-on | **1 didactic message / week** if `weekly_education_opt_in` | 1 shared text / week + M sends |

## Shared copy (broadcast)

For scheduled recommendation or education blasts:

1. Generate **one** Portuguese text per slot (or pick catalog + one IA polish pass).
2. Persist batch (`RecommendationBatch` / content record — see roadmap tasks).
3. Enqueue Cloud Tasks with the **same body** per eligible phone.

Do **not** call Claude once per subscriber for the same campaign slot.

## Payments

Provider **not chosen**. See [payments-evaluation.md](./payments-evaluation.md) and [adrs/0003-payment-provider.md](./adrs/0003-payment-provider.md).

Until integrated: manual payment + operator activates tier via customer API.

## LGPD (Brazil)

Privacy/terms, export/delete, subprocessors — tracked in [COMMERCIAL-LAUNCH.md](./COMMERCIAL-LAUNCH.md) Phase 8.

## Subprocessors (baseline)

- Twilio (WhatsApp)
- Google Cloud (Run, Datastore, Tasks, Scheduler)
- Anthropic (Claude)
- Payment provider — TBD after ADR 0003

## Related

- [COMMERCIAL-LAUNCH.md](./COMMERCIAL-LAUNCH.md)
- [ROADMAP-TASKS.md](./ROADMAP-TASKS.md)
- Product milestones: [ROADMAP.md](./ROADMAP.md)
