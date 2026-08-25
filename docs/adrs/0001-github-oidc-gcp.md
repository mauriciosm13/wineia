# ADR 0001: GitHub OIDC for GCP Deployments

**Status:** Accepted  
**Date:** 2026-08-24  
**Deciders:** WineAI team  
**Related RFC:** [RFC 0001 — Engineering Foundation](../rfcs/0001-engineering-foundation.md)

---

## Context

WineAI deploys a single Cloud Run service (`wine-concierge`) in project `wineia-490200`, region `southamerica-east1`. CI/CD must push Docker images to Artifact Registry and update Cloud Run without storing long-lived GCP service account JSON keys in GitHub Secrets.

GitHub Actions supports **OpenID Connect (OIDC)** to authenticate to Google Cloud via **Workload Identity Federation (WIF)**. The deploy workflow (`.github/workflows/deploy.yml`) uses `google-github-actions/auth@v2` with repository variables `WIF_PROVIDER` and `WIF_SERVICE_ACCOUNT`.

Local operators may still use `gcloud` user credentials via `./deploy.sh`; that path is separate from CI/CD.

---

## Decision

Use **GitHub OIDC → Workload Identity Federation → GCP service account** for all automated deploys. Do **not** commit or store downloadable JSON key files for CI.

The deploy workflow:

1. Requests an OIDC token (`permissions.id-token: write`)
2. Exchanges it for GCP credentials via the configured WIF provider
3. Impersonates the deploy service account to push images and run `gcloud run deploy`

Deploy triggers are **version tags** (`v*.*.*`) and **workflow_dispatch** only — not every push to `main`.

---

## Consequences

### Positive

- No JSON keys in GitHub Secrets to rotate or leak
- Short-lived tokens per workflow run
- Aligns with GCP security best practices

### Negative

- One-time WIF pool/provider and IAM binding setup required
- Misconfigured provider or SA roles cause opaque deploy failures until IAM is corrected

### Neutral

- GitHub Environment `production` can gate deploy with optional approval
- Repository variables must be set: `WIF_PROVIDER`, `WIF_SERVICE_ACCOUNT`

---

## Alternatives

| Alternative | Why not chosen |
|-------------|----------------|
| Service account JSON in `GCP_SA_KEY` secret | Higher leak and rotation risk |
| Deploy from developer laptops only | No repeatable, auditable release path |
| Cloud Build triggers on GitHub | Extra service; team standardized on GitHub Actions |

---

## Tradeoffs

WIF adds initial setup complexity but removes persistent credential storage. Single-environment prod means tag/manual deploy is mandatory — acceptable because there is no staging slot to auto-promote.

---

## IAM roles (deploy service account)

Minimum roles for the GitHub-linked service account:

| Role | Purpose |
|------|---------|
| `roles/run.admin` | Deploy and update Cloud Run services |
| `roles/artifactregistry.writer` | Push container images |
| `roles/iam.serviceAccountUser` | Act as runtime service account if needed |

See [DEPLOYMENT.md](../DEPLOYMENT.md) for WIF and Artifact Registry setup steps.

---

## References

- [Google Cloud: Workload Identity Federation with GitHub Actions](https://cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines)
- [google-github-actions/auth](https://github.com/google-github-actions/auth)
