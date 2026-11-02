# ADR 0004: Secret Manager for Cloud Run runtime secrets

**Status:** Accepted  
**Date:** 2026-11-02  
**Deciders:** WineAI team  
**Related:** T011 · [COMMERCIAL-LAUNCH.md](../COMMERCIAL-LAUNCH.md) Phase 2 #8 · [SECRET-MANAGER-MIGRATION.md](../operations/SECRET-MANAGER-MIGRATION.md)

---

## Context

Production `wine-concierge` (Cloud Run, project `wineia-490200`) needs Twilio credentials, Anthropic API keys, and `JOB_INTERNAL_SECRET` for job/worker routes. Today:

- Some values are set as **plain Cloud Run environment variables** (`core/config.py`).
- Claude and parts of Twilio still load from **gitignored `config.json`** via `core/utils/load_config.py`, which must not contain production secrets in the container image.
- [DEPLOYMENT.md](../DEPLOYMENT.md) already recommends Secret Manager but lacked a mapping and rollout procedure.

CI/CD deploy uses GitHub OIDC (ADR 0001) and does not inject application secrets from GitHub — correct for app secrets, but ops need a single GCP-native store.

---

## Decision

1. Store production-sensitive values in **Google Secret Manager** in `wineia-490200`, using secret ids under the `wine-concierge/` prefix (see migration runbook).
2. Expose secrets to the app as **Cloud Run environment variables** via secret references (`--set-secrets`), keeping **existing env var names** (`TWILIO_AUTH_TOKEN`, `JOB_INTERNAL_SECRET`, etc.) so current Python code continues to work without change during cutover.
3. Grant the **Cloud Run runtime service account** `roles/secretmanager.secretAccessor` on required secrets only.
4. **Do not** fetch secrets at runtime with the Secret Manager API in application code in the initial migration (no new dependency or latency on cold start). Revisit if dynamic rotation without redeploy becomes a requirement.
5. **Local development** continues to use `config.json` and optional local env vars; Secret Manager is production-only.

Follow-up engineering (out of T011 scope): unify Claude/Twilio on env-first loading so production does not depend on `config.json`.

---

## Consequences

### Positive

- Central rotation and audit trail in GCP
- No secrets in GitHub Actions or deploy YAML
- Aligns with COMMERCIAL-LAUNCH security gate #8

### Negative

- Ops must run phased cutover and keep Scheduler headers in sync with `JOB_INTERNAL_SECRET`
- Deploy workflow does not yet automate `--set-secrets`; manual or future CD update required

### Neutral

- Secret naming and IAM documented in [SECRET-MANAGER-MIGRATION.md](../operations/SECRET-MANAGER-MIGRATION.md)

---

## Alternatives

| Alternative | Why not chosen |
|-------------|----------------|
| Plain env vars only | No versioning/audit; easy to leak in console exports |
| Secret Manager API in app | Extra code, cold-start latency, IAM in app layer |
| GitHub Actions secrets for runtime | Wrong layer; does not help Cloud Run at runtime |
| Bake `config.json` in image | Violates repo policy; secrets in Artifact Registry layers |

---

## References

- [Configure secrets for Cloud Run services](https://cloud.google.com/run/docs/configuring/services/secrets)
- [SECRET-MANAGER-MIGRATION.md](../operations/SECRET-MANAGER-MIGRATION.md)
