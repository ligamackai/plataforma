#!/bin/bash
set -e

PROJECT_ID="mackai-468422"
REGION="us-central1"
SERVICE="plataforma"
IMAGE="gcr.io/$PROJECT_ID/plataforma:v1.0.0"
ICN="$PROJECT_ID:$REGION:mackai-postgre"

WORKDIR="/tmp/plataforma-deploy"

gcloud config set project "$PROJECT_ID"
gcloud auth application-default set-quota-project "$PROJECT_ID"

rm -rf "$WORKDIR"
git clone https://github.com/ligamackai/plataforma.git "$WORKDIR"

cd "$WORKDIR/imagem"

gcloud builds submit --tag "$IMAGE"

gcloud run deploy "$SERVICE" \
  --image "$IMAGE" \
  --region "$REGION" \
  --timeout 600s \
  --add-cloudsql-instances="$ICN" \
  --set-env-vars PROJECT_ID="$PROJECT_ID" \
  --set-env-vars REGION="$REGION" \
  --set-env-vars DB_USER=plataforma_beta \
  --set-env-vars DB_PASSWORD=senha123 \
  --set-env-vars DB_NAME=plataforma_beta \
  --set-env-vars DB_SCHEMA=plataforma \
  --set-env-vars DB_HOST="/cloudsql/$ICN" \
  --set-env-vars DB_PORT=5432 \
  --set-env-vars BUCKET=plataforma-mackai \
  --set-env-vars SMTP_USER=rafavidal1709@gmail.com \
  --set-secrets SMTP_PASSWORD=smtp-password:latest \
  --allow-unauthenticated

echo "\n\n✅✅✅ Deploy concluído! ✅✅✅"

echo "\n\n🧹 Limpando imagens antigas de plataforma..."
DIGESTS_LLMA=$(gcloud container images list-tags gcr.io/mackai-468422/plataforma \
  --sort-by=~TIMESTAMP \
  --format='get(digest)' | tail -n +3)

if [ -z "$DIGESTS_LLMA" ]; then
  echo "Nenhuma imagem antiga para limpar em plataforma."
else
  echo "$DIGESTS_LLMA" | xargs -I {} gcloud container images delete -q gcr.io/mackai-468422/plataforma@{}
fi

echo "\n\n✅✅✅ Limpeza concluída! ✅✅✅"

read -p "Pressione ENTER para sair..."

