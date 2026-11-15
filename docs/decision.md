# Relatório de decisões — arquitetura WineAI

**Data:** 14 de novembro de 2026 (America/Sao_Paulo)  
**Escopo:** decisões já aceitas no repositório, caminho da requisição até a regra de negócio, fases de validação e gaps de segurança ainda abertos.

A arquitetura está indo para um backend único no Cloud Run, com regra de produto isolada no domínio e com três controles de volume separados: abuso de webhook, cota de conversa sob demanda e cadência de envio agendado. A URL não chega na regra de negócio direto. Entre elas ficam duas camadas de aplicação.

## Camadas entre a URL e a regra

O pedido entra pelo WSGI (`main` + gunicorn) e atravessa exatamente duas camadas antes do domínio:

1. **Roteador** (`api/routes.py`). Escolhe o handler e aplica portões que valem para várias rotas: segredo interno em `/jobs/*` e `/workers/*`, e limite por IP no webhook.
2. **Handler** (`api/handlers/*`). Lê o HTTP, valida o protocolo (assinatura Twilio, JSON, telefone) e monta as dependências (Datastore, Twilio, Claude). Não deve conter política de plano.

A regra de negócio fica em `domain/` (serviços, cadência, entitlements, modelo de cliente). `infrastructure/` só executa o efeito depois da decisão: gravar no Datastore, chamar a Twilio, chamar o Claude ou enfileirar uma task. `core/` é configuração e utilitário compartilhado. O domínio não importa infraestrutura.

No webhook do WhatsApp o caminho concreto é:

`POST /webhook/whatsapp` → limite por IP no roteador → assinatura Twilio e limite por telefone no handler → `process_incoming_message` → `can_send_on_demand` → Claude no request → enqueue Cloud Tasks → worker Twilio.

## Em quantas fases a validação está definida

São quatro fases, de propósito em lugares diferentes.

| Fase | Onde | O que decide | Exemplo |
|------|------|----------------|---------|
| 1. Portão de transporte | Roteador | Quem pode chamar a rota | `X-Job-Internal-Secret` com comparação em tempo constante; se o segredo não existe, a rota fecha |
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
- Cota sob demanda por tier, com reset no calendário UTC na leitura do cliente (T024): ENTRY 2/dia, SUPERIOR 10/dia.
- Cadência agendada: janela de 168 h, no máximo 2 envios, com guarda de 24 h para retry do Scheduler não duplicar o mesmo slot (T021).
- Provedor de pagamento ainda não foi escolhido ([ADR 0003](./adrs/0003-payment-provider.md), status proposto). Até lá, ativação de plano é manual pela API de cliente.

### Processo

- Sem commit direto em `main`. Commits no formato Conventional Commits. Cobertura de domínio/core com piso de 95%.

## Gaps de segurança que ainda existem

O modelo de ameaça em [threat-model.md](./threat-model.md) fica atrás do código em pontos já entregues (rate limit do webhook, cota por tier, worker de campanha, Scheduler no CD). Os buracos abaixo continuam reais.

**Superfície sem autenticação de aplicação.** `GET/POST/PATCH /customers*`, `POST /ia/suggestions` e `POST /recommendation-contents` não exigem segredo nem assinatura. Quem alcançar a URL do Cloud Run lê e altera cliente, dispara Claude e, em `/ia/suggestions`, pode enviar WhatsApp. A proteção prevista hoje é de rede (ingress do Cloud Run, IAP ou gateway), e isso não está no código.

**Limite de abuso é local e burlável.** O contador de IP/telefone vive na memória de cada instância do Cloud Run. Várias instâncias multiplicam o teto. O IP vem de `X-Forwarded-For` quando o header existe, então um cliente pode escolher o IP que entra na chave do limite. A assinatura da Twilio continua obrigatória; o que se perde é o freio de volume.

**Um segredo único para jobs e workers.** Quem vaza `JOB_INTERNAL_SECRET` dispara recomendação, educação, campanha e envio em massa até a rotação. O CD grava esse valor como header estático no Cloud Scheduler ([ADR 0005](./adrs/0005-cloud-scheduler-from-cd.md)): quem tem `cloudscheduler.jobs.get` enxerga o segredo. Não há token OIDC no alvo do Scheduler.

**Webhook ainda gasta Claude no request.** O Twilio de produto saiu do request (T032), mas cada POST válido ainda pode chamar Claude de forma síncrona. Não há disjuntor global de gasto (T061). Injeção de prompt depende de prompt fixo mais regex; isso reduz o óbvio e não cobre jailbreak. `/ia/suggestions` ainda pode enviar WhatsApp de forma síncrona.

**URL da assinatura Twilio depende de `X-Forwarded-Proto` e `Host`.** Se o proxy reescrever host ou esquema de um jeito diferente do que a Twilio assinou, webhooks legítimos caem em 403. Forjar uma assinatura válida exige o auth token.

**Segredos e IAM ainda em transição.** O ADR 0004 aceita o Secret Manager, mas o workflow de deploy ainda não aplica `--set-secrets` em todas as credenciais de runtime. Parte do Claude/Twilio ainda sabe ler `config.json`. A service account do Cloud Run com IAM largo demais está anotada como item em aberto (CL #11). O deploy ganhou leitura do segredo de job para configurar o Scheduler.

**O que ainda não existe e abre superfície nova.** Pagamento (webhook de provedor, T042), exportação e exclusão LGPD (T050–T051) e proteção de branch no GitHub (T004, fora do código). Quando o webhook de pagamento entrar, será mais um ponto público sem o modelo de assinatura da Twilio.

## Leitura em uma frase

A URL para em duas camadas finas (rota e handler) que só autenticam e limitam abuso; a decisão de “este cliente pode receber isto” fica no domínio, em contadores separados; o que ainda falta para esse desenho fechar é tirar as APIs de operador da internet aberta, tornar o limite de abuso global e tirar o segredo do header visível do Scheduler.
