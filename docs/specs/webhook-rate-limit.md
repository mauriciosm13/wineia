# Spec — WhatsApp webhook rate limiting

**Status:** implemented (T012 / COMMERCIAL-LAUNCH #10)  
**Scope:** `POST /webhook/whatsapp` only

## Goals

- Reduce webhook abuse (credential stuffing, LLM cost amplification) without blocking legitimate Twilio traffic under normal load.
- Fail with **429 Too Many Requests** and JSON body when a limit is exceeded.

## Limits

Two independent **sliding-window** counters (in-process, per Cloud Run instance / gunicorn worker):

| Dimension | Env var (max) | Env var (window sec) | Default max | Default window |
|-----------|---------------|----------------------|-------------|----------------|
| Client IP | `WEBHOOK_RATE_LIMIT_IP_MAX` | `WEBHOOK_RATE_LIMIT_IP_WINDOW_SECONDS` | 120 | 60 |
| Sender phone | `WEBHOOK_RATE_LIMIT_PHONE_MAX` | `WEBHOOK_RATE_LIMIT_PHONE_WINDOW_SECONDS` | 30 | 60 |

Set **`_*_MAX=0`** to disable that dimension.

IP is taken from `X-Forwarded-For` (first hop) when present, else `REMOTE_ADDR`.

Phone is normalized from the Twilio payload (`WaId` / `From`) **after** signature validation.

## Request flow

```
POST /webhook/whatsapp
  → IP limit (api/routes.py)
  → handler: read body, validate Twilio signature (403 if invalid)
  → phone limit (if phone present)
  → domain messaging logic
```

## Responses

| Condition | Status | Body |
|-----------|--------|------|
| IP limited | 429 | `{"error":"rate_limit_exceeded"}` |
| Invalid signature | 403 | `{"error":"invalid signature"}` |
| Phone limited | 429 | `{"error":"rate_limit_exceeded"}` |
| OK | 200 | `{"status":"received"}` |

## Operations notes

- Limits are **not shared** across Cloud Run instances or gunicorn workers; edge/WAF rate limiting may still be added later.
- Twilio retries on 429; keep defaults high enough for normal retries and bursts.
- Tune via Cloud Run env vars; see [DEPLOYMENT.md](../DEPLOYMENT.md) and [operations/PRODUCTION.md](../operations/PRODUCTION.md).

## Code map

| Module | Role |
|--------|------|
| `core/rate_limit.py` | `SlidingWindowRateLimiter` |
| `api/webhook_rate_limit.py` | Config wiring, IP/phone checks, 429 helper |
| `api/routes.py` | IP guard |
| `api/handlers/whatsapp_handler.py` | Phone guard |
