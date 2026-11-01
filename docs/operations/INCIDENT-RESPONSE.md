# Incident response — WineAI

1. Scope: all users vs one number vs one endpoint?
2. Read [PRODUCTION.md](./PRODUCTION.md) for expected flows.
3. Tail logs — [OBSERVABILITY.md](./OBSERVABILITY.md).
4. Match symptom below.

## Symptoms

### 404 on `/health`

- Wrong URL or trailing slash (exact path match).
- Wrong Cloud Run revision — check traffic split.

### Twilio webhook failures

- Signature validation failing — Twilio auth token vs env.
- Check Twilio debugger + Cloud Run logs for POST body.

### Messages not sent

- Customer `CANCELED` or daily cap hit.
- Twilio credentials; worker `/workers/send-message` errors.
- Cloud Tasks: `SERVICE_URL`, queue IAM, task target 404.

### Recommendations job empty

- No active customers; selector/content pool exhausted.
- Job endpoint auth (if secret added later).
- Claude API errors — check logs in `ia_service` / recommendation services.

### Deploy regression

- Roll back traffic to previous revision ([DEPLOYMENT.md](../DEPLOYMENT.md)).
- Redeploy previous tag.

## Rollback

```bash
gcloud run revisions list --service=wine-concierge \
  --region=southamerica-east1 --project=wineia-490200

gcloud run services update-traffic wine-concierge \
  --to-revisions=REVISION=100 \
  --region=southamerica-east1 --project=wineia-490200
```

## Subagent report

Include: symptom, revision, log snippet, layer (Twilio | Run | Datastore | Claude | Tasks), suggested roadmap task id from [ROADMAP-TASKS.md](../ROADMAP-TASKS.md).
