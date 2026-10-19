#!/usr/bin/env bash
#
# Script automatisé de build des images Docker pour PROJECT RESILIENCE-ALPHA
# Usage: ./scripts/build-images.sh [--tag <tag>] [--service <name>] [--no-cache]
#

set -e

TAG="latest"
SERVICE="all"
NO_CACHE=""

# Couleurs
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

while [[ $# -gt 0 ]]; do
  case $1 in
    --tag|-t)
      TAG="$2"
      shift 2
      ;;
    --service|-s)
      SERVICE="$2"
      shift 2
      ;;
    --no-cache)
      NO_CACHE="--no-cache"
      shift
      ;;
    *)
      echo -e "${RED}[ERROR] Option inconnue: $1${NC}"
      exit 1
      ;;
  esac
done

echo -e "${CYAN}==========================================================${NC}"
echo -e "${CYAN}  PROJECT RESILIENCE-ALPHA — DOCKER IMAGE BUILDER         ${NC}"
echo -e "${CYAN}  Tag cible : $TAG | Service : $SERVICE                   ${NC}"
echo -e "${CYAN}==========================================================${NC}"

# Vérifier Docker
if ! docker info > /dev/null 2>&1; then
  echo -e "${RED}[ERROR] Le moteur Docker n'est pas démarré ou n'est pas accessible.${NC}"
  exit 1
fi

build_image() {
  local name="$1"
  local context="$2"
  local full_tag="${name}:${TAG}"

  echo -e "\n${YELLOW}----------------------------------------------------------${NC}"
  echo -e "${CYAN}[INFO] Construction de l'image : ${full_tag} (${context})${NC}"
  
  start_time=$(date +%s)
  docker build ${NO_CACHE} -t "${full_tag}" "${context}"
  end_time=$(date +%s)
  duration=$((end_time - start_time))

  echo -e "${GREEN}[SUCCESS] Image ${full_tag} construite en ${duration}s.${NC}"
}

if [[ "$SERVICE" == "all" || "$SERVICE" == "payment-api" ]]; then
  build_image "payment-api" "services/payment-api"
fi

if [[ "$SERVICE" == "all" || "$SERVICE" == "remediation-engine" ]]; then
  build_image "remediation-engine" "services/remediation-engine"
fi

if [[ "$SERVICE" == "all" || "$SERVICE" == "dashboard-ui" ]]; then
  build_image "dashboard-ui" "services/dashboard-ui"
fi

echo -e "\n${GREEN}==========================================================${NC}"
echo -e "${GREEN}  BUILD TERMINÉ AVEC SUCCÈS !                             ${NC}"
echo -e "${GREEN}==========================================================${NC}"
docker images | grep -E "payment-api|remediation-engine|dashboard-ui" | grep "${TAG}" || true
