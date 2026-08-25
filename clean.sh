#!/bin/bash

# Configurações
PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project)}"
REGION="${REGION:-southamerica-east1}"

echo "Projeto: $PROJECT_ID"
echo "Região: $REGION"
echo ""

# Lista todos os serviços do Cloud Run
SERVICES=$(gcloud run services list \
  --project="$PROJECT_ID" \
  --region="$REGION" \
  --format="value(metadata.name)")

if [ -z "$SERVICES" ]; then
  echo "Nenhum serviço encontrado."
  exit 0
fi

for SERVICE in $SERVICES; do
  echo "==> Serviço: $SERVICE"

  # Obtém a revisão ativa atual
  ACTIVE_REVISION=$(gcloud run services describe "$SERVICE" \
    --project="$PROJECT_ID" \
    --region="$REGION" \
    --format="value(status.traffic[0].revisionName)")

  echo "    Revisão ativa: $ACTIVE_REVISION"

  # Lista todas as revisões do serviço
  REVISIONS=$(gcloud run revisions list \
    --service="$SERVICE" \
    --project="$PROJECT_ID" \
    --region="$REGION" \
    --format="value(metadata.name)")

  for REVISION in $REVISIONS; do
    if [ "$REVISION" != "$ACTIVE_REVISION" ]; then
      echo "    Deletando revisão: $REVISION"
      gcloud run revisions delete "$REVISION" \
        --project="$PROJECT_ID" \
        --region="$REGION" \
        --quiet
    else
      echo "    Mantendo revisão ativa: $REVISION"
    fi
  done

  echo ""
done

echo "Limpeza concluída!"