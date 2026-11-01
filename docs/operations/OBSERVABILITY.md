# Observability — WineAI

## Cloud Run logs

```bash
gcloud run services logs tail wine-concierge \
  --region=southamerica-east1 --project=wineia-490200
```

Structured request logging: `log_request(method, path)` in router.

## CI artifacts

PR builds upload `coverage.xml` (workflow `ci.yml`).

## Twilio

Twilio Console → Monitor → Logs for delivery errors not visible in app code.

## Datastore

Console → inspect Customer / pre-sale / recommendation entities.

## Gaps (planned)

- Request correlation IDs
- Dashboards for send failures and Claude token usage
- Alerts on job failure

See COMMERCIAL-LAUNCH Phase 2 and ROADMAP M6.
