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
QUEUES=("wine-messages")
SCHEDULER_JOBS=("daily-recommendations")

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
# 3. Build com cache remoto (BuildKit)
# ─────────────────────────────────────────
log "Fazendo build com cache remoto..."

GIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "latest")
IMAGE_VERSIONED="$IMAGE:$GIT_SHA"
IMAGE_LATEST="$IMAGE:latest"

export DOCKER_BUILDKIT=1

docker build \
  --platform linux/amd64 \
  --cache-from "$IMAGE_LATEST" \
  --build-arg BUILDKIT_INLINE_CACHE=1 \
  -t "$IMAGE_VERSIONED" \
  -t "$IMAGE_LATEST" \
  .

ok "Build concluído: $IMAGE_VERSIONED"

# ─────────────────────────────────────────
# 4. Push para o Artifact Registry
# ─────────────────────────────────────────
log "Enviando imagem para o Artifact Registry..."
docker push "$IMAGE_VERSIONED"
docker push "$IMAGE_LATEST"
ok "Push concluído."

# ─────────────────────────────────────────
# 5. Deploy no Cloud Run
# ─────────────────────────────────────────
log "Iniciando deploy no Cloud Run..."

gcloud run deploy "$SERVICE_NAME" \
  --image "$IMAGE_VERSIONED" \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --no-traffic \
  --project "$PROJECT_ID"

gcloud run services update-traffic "$SERVICE_NAME" \
  --to-latest \
  --region "$REGION" \
  --project "$PROJECT_ID"

ok "Deploy finalizado com sucesso! 🍷"



wait
ok "Infraestrutura verificada."