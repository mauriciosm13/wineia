#!/bin/bash

set -e

# ─────────────────────────────────────────
# Configurações
# ─────────────────────────────────────────
PROJECT_ID="wineia-490200"
SERVICE_NAME="wine-concierge"
REGION="southamerica-east1"
REGISTRY="southamerica-east1-docker.pkg.dev"
IMAGE="$REGISTRY/$PROJECT_ID/$SERVICE_NAME/$SERVICE_NAME"

QUEUE_REGION="$REGION"

# filas do sistema
QUEUES=(
  "wine-messages"
)

# cron jobs
SCHEDULER_JOBS=(
  "daily-recommendations"
)

# ─────────────────────────────────────────
# Funções auxiliares
# ─────────────────────────────────────────
log()  { echo -e "\033[1;34m[INFO]\033[0m  $1"; }
ok()   { echo -e "\033[1;32m[OK]\033[0m    $1"; }
err()  { echo -e "\033[1;31m[ERRO]\033[0m  $1"; exit 1; }

# ─────────────────────────────────────────
# 1. Verifica dependências
# ─────────────────────────────────────────
log "Verificando dependências..."
command -v gcloud &>/dev/null || err "gcloud CLI não encontrado. Instale o Google Cloud SDK."
command -v docker  &>/dev/null || err "Docker não encontrado."

# ─────────────────────────────────────────
# 2. Autentica no Artifact Registry
# ─────────────────────────────────────────
log "Autenticando no Artifact Registry..."
gcloud auth configure-docker "$REGISTRY" --quiet
ok "Autenticação concluída."

# ─────────────────────────────────────────
# 3. Build da imagem Docker
# ─────────────────────────────────────────
log "Fazendo build da imagem Docker (linux/amd64)..."
docker build --platform linux/amd64 -t "$IMAGE" .
ok "Build concluído: $IMAGE"

# ─────────────────────────────────────────
# 4. Push para o Artifact Registry
# ─────────────────────────────────────────
log "Enviando imagem para o Artifact Registry..."
docker push "$IMAGE"
ok "Push concluído."

# ─────────────────────────────────────────
# 5. Deploy no Cloud Run
# ─────────────────────────────────────────
log "Iniciando deploy no Cloud Run..."

gcloud run deploy "$SERVICE_NAME" \
  --image "$IMAGE" \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --project "$PROJECT_ID"

ok "Deploy finalizado com sucesso! 🍷"

# ─────────────────────────────────────────
# 6. Criação das filas (Cloud Tasks)
# ─────────────────────────────────────────
log "Verificando filas do Cloud Tasks..."

for QUEUE in "${QUEUES[@]}"; do

  if gcloud tasks queues describe "$QUEUE" \
      --location "$QUEUE_REGION" \
      --project "$PROJECT_ID" &>/dev/null; then

      ok "Fila '$QUEUE' já existe."

  else

      log "Criando fila '$QUEUE'..."

      gcloud tasks queues create "$QUEUE" \
        --location "$QUEUE_REGION" \
        --project "$PROJECT_ID"

      ok "Fila '$QUEUE' criada."

  fi

done

# ─────────────────────────────────────────
# 7. Criação de jobs do Scheduler
# ─────────────────────────────────────────
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
  --region "$REGION" \
  --project "$PROJECT_ID" \
  --format "value(status.url)")

for JOB in "${SCHEDULER_JOBS[@]}"; do

  if gcloud scheduler jobs describe "$JOB" \
      --location "$REGION" \
      --project "$PROJECT_ID" &>/dev/null; then

      ok "Scheduler job '$JOB' já existe."

  else

      log "Criando scheduler job '$JOB'..."

      gcloud scheduler jobs create http "$JOB" \
        --schedule="0 10 * * *" \
        --uri="$SERVICE_URL/jobs/daily-recommendations" \
        --http-method=POST \
        --location="$REGION" \
        --project="$PROJECT_ID"

      ok "Scheduler job '$JOB' criado."

  fi

done