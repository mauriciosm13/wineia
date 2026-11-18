# Relatório de decisões — arquitetura WineAI

**Data:** 14 de novembro de 2026 (America/Sao_Paulo)  
**Escopo:** decisões já aceitas no repositório, caminho da requisição até a regra de negócio, fases de validação e gaps de segurança ainda abertos.

A arquitetura está indo para um backend único no Cloud Run, com regra de produto isolada no domínio e com três controles de volume separados: abuso de webhook, cota de conversa sob demanda e cadência de envio agendado. A URL não chega na regra de negócio direto. Entre elas ficam duas camadas de aplicação.

## Camadas entre a URL e a regra

O pedido entra pelo WSGI (`main` + gunicorn) e atravessa exatamente duas camadas antes do domínio:

1. **Router** (`api/routes.py`). Picks the handler and applies cross-route gates: shared internal secret on `/jobs/*`, `/workers/*`, `/customers*`, `/ia/suggestions`, and `/recommendation-contents` (T072); IP rate limit on the webhook.
2. **Handler** (`api/handlers/*`). Reads HTTP, validates protocol (Twilio signature, JSON, phone) and wires dependencies (Datastore, Twilio, Claude). Must not own plan policy.

A regra de negócio fica em `domain/` (serviços, cadência, entitlements, modelo de cliente). `infrastructure/` só executa o efeito depois da decisão: gravar no Datastore, chamar a Twilio, chamar o Claude ou enfileirar uma task. `core/` é configuração e utilitário compartilhado. O domínio não importa infraestrutura.

No webhook do WhatsApp o caminho concreto é:

`POST /webhook/whatsapp` → limite por IP no roteador → assinatura Twilio e limite por telefone no handler → `process_incoming_message` → `can_send_on_demand` → Claude no request → enqueue Cloud Tasks → worker Twilio.

## Em quantas fases a validação está definida

São quatro fases, de propósito em lugares diferentes.

| Fase | Onde | O que decide | Exemplo |
|------|------|----------------|---------|
| 1. Transport gate | Router | Who may call the route | `X-Job-Internal-Secret` with constant-time compare on jobs, workers, and operator APIs; if the secret is unset, gated routes fail closed |
| 2. Autenticidade do protocolo | Handler | Se o corpo veio de quem diz ter vindo | HMAC da Twilio; sem token, a assinatura falha |
| 3. Abuso de infraestrutura | Roteador + handler | Volume, independente de plano | 120 req/min por IP antes do handler; 30 req/min por telefone depois da assinatura; resposta 429 |
| 4. Política de produto | Domínio | Se este cliente pode receber esta mensagem | Status `active`, cota diária ENTRY 2 / SUPERIOR 10 (UTC), cadência de 2 recomendações em janela de 168 h, opt-in da educação semanal |

Há um filtro extra dentro da fase 4, no caminho de IA: `sanitize_input` (tamanho e lista de padrões) e `validate_output` antes de devolver texto ao WhatsApp. Isso não é autenticação; é higiene do prompt.

Essas fases não se substituem. O limite do webhook (fase 3) não conta mensagem de campanha. A cota sob demanda não incrementa no envio agendado. A cadência semanal não usa `messages_sent_today`.

## Decisões técnicas já tomadas

### Forma do sistema

- Clean Architecture com dependência para dentro: `api` → `domain` → `infrastructure`.
- Um único ambiente de produção: Cloud Run `wine-concierge` em `southamerica-east1`. Merge em `main` não publica. Publicação é tag `v*.*.*` ou `workflow_dispatch`.
- Deploy automatizado usa OIDC do GitHub para o GCP ([ADR 0001](./adrs/0001-github-oidc-gcp.md)). Não há chave JSON de service account no GitHub.
- Persistência em Datastore. Testes de CI usam fakes em memória, sem emulador ([ADR 0002](./adrs/0002-unit-tests-pure-mocks.md)).
- Segredos de produção ficam no Secret Manager e entram no Cloud Run como variáveis de ambiente com os mesmos nomes de hoje. O código não chama a API do Secret Manager em runtime ([ADR 0004](./adrs/0004-secret-manager-runtime-secrets.md)). Desenvolvimento local continua com `config.json`.
- Saída para o WhatsApp é assíncrona: Scheduler → job → Cloud Tasks → worker → Twilio; e no webhook, Claude permanece no request enquanto o texto de produto (resposta IA e aviso de limite) vai para Cloud Tasks `send_message` → `POST /workers/send-message` (T032). As filas estão nomeadas (`wine-messages`, `wine-campaigns`). O worker `POST /workers/send-campaign` existe e exige o mesmo segredo interno (T030). O CD cria os jobs do Cloud Scheduler para recomendação e educação semanal e grava o header `X-Job-Internal-Secret` a partir do Secret Manager ([ADR 0005](./adrs/0005-cloud-scheduler-from-cd.md), T031).

### Produto e custo de IA

- Planos estáveis no dado: `ENTRY` e `SUPERIOR`, mais `weekly_education_opt_in`.
- Recomendação e educação agendadas geram um texto de Claude por execução e replicam o mesmo corpo para todos os elegíveis.
- Cota sob demanda por tier, com reset no calendário UTC na leitura do cliente (T024): defaults ENTRY 2/dia, SUPERIOR 10/dia; limites ajustáveis por env (`ON_DEMAND_DAILY_LIMIT_ENTRY` / `ON_DEMAND_DAILY_LIMIT_SUPERIOR`) via `core/config` (T060). Teto global de chamadas Claude por dia UTC via `CLAUDE_DAILY_CALL_BUDGET` (`0`/unset = ilimitado; `> 0` falha fechado antes de gerar) (T061).
- Cadência agendada: janela de 168 h, no máximo 2 envios, com guarda de 24 h para retry do Scheduler não duplicar o mesmo slot (T021).
- Provedor de pagamento ainda não foi escolhido ([ADR 0003](./adrs/0003-payment-provider.md), status proposto). Até lá, ativação de plano é manual pela API de cliente.

### Processo

- Sem commit direto em `main`. Commits no formato Conventional Commits. Cobertura de domínio/core com piso de 95%.

## Remaining security gaps

The threat model in [threat-model.md](./threat-model.md) tracks delivered controls (webhook rate limit, tier quotas, campaign worker, Scheduler in CD, operator API auth). Open gaps below remain real.

**Operator APIs authenticated (T072 — closed).** `/customers*`, `/ia/suggestions`, and `/recommendation-contents` require the same `JOB_INTERNAL_SECRET` + `X-Job-Internal-Secret` as jobs/workers, with fail-closed behavior when unset. Network controls (Cloud Run ingress / IAP) remain recommended as defense in depth.

**Abuse limits are local and bypassable.** IP/phone counters live in each Cloud Run instance memory. Multiple instances multiply the ceiling. IP comes from `X-Forwarded-For` when present, so a client can choose the IP key. Twilio signature remains mandatory; what weakens is the volume brake.

**One shared secret for jobs, workers, and operator APIs.** A leak of `JOB_INTERNAL_SECRET` grants recommendation, education, campaign, mass send, customer CRUD/export/erase, IA suggestions, and catalog writes until rotation. CD writes that value as a static header on Cloud Scheduler ([ADR 0005](./adrs/0005-cloud-scheduler-from-cd.md)): anyone with `cloudscheduler.jobs.get` can read the secret. No OIDC token on the Scheduler target.

**Webhook still spends Claude in-request.** Product Twilio left the request (T032), but each valid POST may still call Claude synchronously. There is a global UTC call-count breaker (`CLAUDE_DAILY_CALL_BUDGET`, T061); no USD budget or PagerDuty alert. Prompt injection relies on a fixed prompt plus regex; that cuts obvious abuse and does not cover jailbreaks. `/ia/suggestions` can still send WhatsApp synchronously (now secret-gated).

**Twilio signature URL depends on `X-Forwarded-Proto` and `Host`.** If a proxy rewrites host or scheme differently from what Twilio signed, legitimate webhooks get 403. Forging a valid signature still requires the auth token.

**Secrets and IAM still in transition.** ADR 0004 accepts Secret Manager, but the deploy workflow may not apply `--set-secrets` for every runtime credential. Some Claude/Twilio paths can still read `config.json`. Over-broad Cloud Run SA IAM remains open (CL #11). Deploy already reads the job secret to configure Scheduler.

**What still does not exist and opens new surface.** Payments (provider webhook, T042) and GitHub branch protection (T004, outside app code). When a payment webhook lands, it will be another public entry without the Twilio signature model. LGPD export/erase (T050–T051) exists and is secret-gated via T072.

## One-line read

The URL stops at two thin layers (route and handler) that authenticate and limit abuse — including operator APIs via the shared job secret (T072); “may this customer receive this” stays in domain counters; what remains is making abuse limits global and removing the secret from the Scheduler-visible static header.
