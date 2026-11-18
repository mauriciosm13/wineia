# WhatsApp / Twilio messaging compliance

Operator notes for commercial launch item **#16** (task **T073**). Spec: [T073-launch-compliance-docs-sdd.md](../specs/sdd/T073-launch-compliance-docs-sdd.md).

This document does **not** register templates in Twilio or Meta. It records how WineAI sends today and what operators must keep aligned with platform policy.

## Templates vs free-form

WhatsApp Business messaging distinguishes:

| Mode | When it applies | WineAI implication |
|------|-----------------|--------------------|
| **Session / free-form** | Typically within the **customer-care window** after the user messages the business (commonly described as ~24 hours; confirm current Meta rules) | Inbound webhook replies (IA answer, daily-limit warning) are user-initiated session traffic when they follow a customer message. |
| **Template (business-initiated)** | Business starts or continues a conversation **outside** the customer-care window | Scheduled recommendations and weekly education are **business-initiated**. Operators must use Meta-approved message templates (via Twilio Content / Messaging) when policy requires templates for that send class. |

WineAI product code today sends **plain text bodies** through Twilio WhatsApp (`infrastructure/external/twilio_whatsapp_client.py`). Before scaling outbound campaigns, confirm each business-initiated path uses an approved template Content SID (or equivalent) where Meta/Twilio require it.

## Opt-in

- Pre-sale create and activation return a Portuguese privacy/terms notice and persist consent metadata (**T050**). Replace placeholder `PRIVACY_POLICY_URL` / `TERMS_OF_SERVICE_URL` before launch.
- Weekly education sends only to customers with `weekly_education_opt_in=true`.
- Do not add customers to outbound recommendation or education cohorts without a clear acquisition / opt-in path.

## Cancelar

Inbound keyword **`cancelar`** updates the customer in Datastore and sends **no** outbound WhatsApp text (T032). Treat cancel as stop of product messaging for that relationship; do not re-engage without a fresh opt-in process that matches policy and product rules.

## 24-hour customer-care window

Meta’s customer-care (session) window governs when free-form replies are allowed after a user message. Rules and exact duration can change — always verify against current Meta and Twilio docs before launch and after provider notices.

Practical WineAI notes:

- **Webhook path:** customer wrote first → free-form session reply is the usual fit (still subject to Twilio delivery and quality rules).
- **Scheduler paths:** recommendations (Thu/Sat) and weekly education (Mon) are not replies inside an open session unless the user happened to message recently. Plan template coverage for those outbound classes.
- A webhook **HTTP 200** after enqueue does not mean WhatsApp already delivered; workers own late send failures ([DEPLOYMENT.md](../DEPLOYMENT.md#whatsapp-webhook-outbound-async-replies)).

## External policy references

Confirm current requirements here (links may move; search Twilio/Meta docs if broken):

- [Twilio WhatsApp best practices / messaging guidelines](https://www.twilio.com/docs/whatsapp/best-practices)
- [Twilio WhatsApp templates overview](https://www.twilio.com/docs/whatsapp/tutorial/send-whatsapp-notification-messages-templates)
- [Meta WhatsApp Business messaging / conversation rules](https://developers.facebook.com/docs/whatsapp/cloud-api/guides/send-messages)
- [Meta message templates](https://developers.facebook.com/docs/whatsapp/business-management-api/message-templates)

## WineAI send paths (current)

| Path | Trigger | Outbound mechanism | Notes |
|------|---------|--------------------|-------|
| Webhook IA reply + daily-limit warning | `POST /webhook/whatsapp` after valid Twilio signature | Enqueue `send_message` → `POST /workers/send-message` → Twilio | Claude runs in the webhook request; Twilio send is async (T032). |
| Cancel | inbound `cancelar` | **No WhatsApp send** | Datastore update only. |
| Scheduled recommendations | Cloud Scheduler → `POST /jobs/send-recommendations` | Fan-out via campaign/message queues → workers → Twilio | Business-initiated; one Claude copy per broadcast slot (T023); ENTRY cadence 2×/week (T021). |
| Weekly education | Cloud Scheduler → `POST /jobs/send-weekly-education` | Queue → workers → Twilio | Business-initiated; opt-in cohort only (T022). |
| `/ia/suggestions` | Operator/internal HTTP | May send WhatsApp **synchronously** | **Must not be public** in production ([threat-model.md](../threat-model.md), [LAUNCH-CHECKLIST.md](../LAUNCH-CHECKLIST.md)). |

Queues: `wine-messages` → `/workers/send-message`; `wine-campaigns` → `/workers/send-campaign`. Job and worker routes require `X-Job-Internal-Secret`.

## Operator checklist (pre-launch)

- [ ] Twilio WhatsApp sender and webhook signature configured for the live Cloud Run URL.
- [ ] Business-initiated template strategy reviewed for recommendations + education (or documented exception with legal/ops sign-off).
- [ ] Privacy/terms URLs are production pages, not placeholders.
- [ ] `/ia/suggestions` is network-restricted.
- [ ] Cancelar behavior verified (status update, no outbound text).

## Related

- [PRODUCTION.md](./PRODUCTION.md)
- [DEPLOYMENT.md](../DEPLOYMENT.md)
- [DATA-RETENTION.md](./DATA-RETENTION.md)
- [COMMERCIAL-LAUNCH.md](../COMMERCIAL-LAUNCH.md) item 16
- [T032 async webhook replies](../specs/sdd/T032-async-webhook-replies-sdd.md)
- [T022 weekly education](../specs/sdd/T022-weekly-education-job-sdd.md)
- [T023 broadcast slot](../specs/sdd/T023-recommendation-broadcast-slot-sdd.md)
