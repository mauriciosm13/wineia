# Builder report — T073 Launch compliance documentation

Comparison contract: [T073-launch-compliance-docs-sdd.md](./T073-launch-compliance-docs-sdd.md).

| ID | Result | Files | What changed |
|----|--------|-------|----------------|
| EW-01 | done | `docs/operations/WHATSAPP-COMPLIANCE.md` | New ops doc: templates vs free-form; opt-in; cancelar (no outbound); 24h window notes; Twilio + Meta policy links; WineAI send paths (webhook queue reply, scheduled recommendations, weekly education, `/ia/suggestions` public-risk note). |
| EW-02 | done | `docs/operations/DATA-RETENTION.md` | New ops doc: Customer/PreSale PII inventory; retention intent; T050/T051 export/erase + `LGPD-EXPORT-DELETE.md`; no payment data yet; Twilio + Anthropic/Claude subprocessors; GCP as processor. |
| EW-03 | done | `docs/DEPLOYMENT.md`, `docs/LAUNCH-CHECKLIST.md`, `docs/operations/PRODUCTION.md` | Document `0`/unset = unlimited; recommend production start **`500`** as ops-tunable guess (DEPLOYMENT + LAUNCH-CHECKLIST required; PRODUCTION config note mirrored for operators). |
| EW-04 | done | `docs/COMMERCIAL-LAUNCH.md` | Checked #16 → WHATSAPP-COMPLIANCE; #61 → DATA-RETENTION. No other CL checkbox flips. |
| EW-05 | done | `docs/ENGINEERING_MANUAL.md`, `docs/LAUNCH-CHECKLIST.md`, `docs/operations/PRODUCTION.md` | ENGINEERING_MANUAL production table lists both docs; LAUNCH-CHECKLIST doc links section lists both; PRODUCTION Related links both. |
| EW-06 | done | `docs/ROADMAP-TASKS.md`, `docs/specs/sdd/INDEX.md`, `docs/specs/sdd/T073-launch-compliance-docs-sdd.md` | Added and checked T073 only; INDEX row `implemented`; SDD status `implemented`. T004 / T040–T043 untouched. |
| EW-07 | done | whole diff | Docs-only (+ CONTEXT.md handoff). No `api/`, `domain/`, `infrastructure/`, or `tests/` product code. No payments implementation. |

## Files touched

| Path | EW |
|------|-----|
| `CONTEXT.md` | handoff (orchestrator) |
| `docs/operations/WHATSAPP-COMPLIANCE.md` (new) | EW-01 |
| `docs/operations/DATA-RETENTION.md` (new) | EW-02 |
| `docs/DEPLOYMENT.md` | EW-03 |
| `docs/LAUNCH-CHECKLIST.md` | EW-03, EW-05 |
| `docs/operations/PRODUCTION.md` | EW-03 (budget note), EW-05 |
| `docs/COMMERCIAL-LAUNCH.md` | EW-04 |
| `docs/ENGINEERING_MANUAL.md` | EW-05 |
| `docs/ROADMAP-TASKS.md` | EW-06 |
| `docs/specs/sdd/INDEX.md` | EW-06 |
| `docs/specs/sdd/T073-launch-compliance-docs-sdd.md` (new) | EW-06 |
| `docs/specs/sdd/T073-builder-report.md` (new) | report |

## Verification

```bash
# From worktree / branch feat/t073-launch-compliance-docs
git diff --name-only origin/main
rg -n 'WHATSAPP-COMPLIANCE|DATA-RETENTION|\*\*500\*\*|T073' \
  docs/COMMERCIAL-LAUNCH.md docs/DEPLOYMENT.md docs/LAUNCH-CHECKLIST.md \
  docs/ENGINEERING_MANUAL.md docs/operations/PRODUCTION.md \
  docs/ROADMAP-TASKS.md docs/specs/sdd/INDEX.md
# Confirm only CL #16 and #61 flipped:
git diff origin/main -- docs/COMMERCIAL-LAUNCH.md
```

Results: docs-only paths as listed; CL diff shows only items 16 and 61; suggested budget `500` present in DEPLOYMENT + LAUNCH-CHECKLIST; new ops docs present.
