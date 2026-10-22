#!/usr/bin/env bash
#
# Script automatisé de build des images Docker pour PROJECT RESILIENCE-ALPHA
# Usage: ./scripts/build-images.sh [--tag <tag>] [--service <name>] [--platform <platform>] [--cluster <kind-cluster>] [--no-cache] [--no-kind-load]
#

set -e

TAG="latest"
SERVICE="all"
PLATFORM=""
NO_CACHE=""
NO_KIND_LOAD="false"
KIND_CLUSTER=""

# Détection automatique de l'architecture Linux selon l'hôte Bash (sh/bash)
if [ -z "$PLATFORM" ]; then
  ARCH=$(uname -m)
  case "$ARCH" in
    x86_64)         PLATFORM="linux/amd64" ;;
    aarch64|arm64)  PLATFORM="linux/arm64" ;;
    *)              PLATFORM="linux/amd64" ;;
  esac
fi

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
    --platform|-p)
      PLATFORM="$2"
      shift 2
      ;;
    --cluster|-c)
      KIND_CLUSTER="$2"
      shift 2
      ;;
    --no-cache)
      NO_CACHE="--no-cache"
      shift
      ;;
    --no-kind-load)
      NO_KIND_LOAD="true"
      shift
      ;;
    *)
      echo -e "${RED}[ERROR] Option inconnue: $1${NC}"
      exit 1
      ;;
  esac
done

# Détection automatique d'un cluster Kind actif
if [ "$NO_KIND_LOAD" != "true" ] && [ -z "$KIND_CLUSTER" ] && command -v kind >/dev/null 2>&1; then
  KIND_CLUSTER=$(kind get clusters 2>/dev/null | head -n 1)
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo -e "${CYAN}==========================================================${NC}"
echo -e "${CYAN}  PROJECT RESILIENCE-ALPHA — DOCKER IMAGE BUILDER         ${NC}"
echo -e "${CYAN}  Tag : $TAG | Service : $SERVICE | Platform : $PLATFORM  ${NC}"
if [ -n "$KIND_CLUSTER" ]; then
  echo -e "${CYAN}  Cluster Kind : $KIND_CLUSTER (auto-load actif)           ${NC}"
fi
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
  local target_dir="${ROOT_DIR}/${context}"

  echo -e "\n${YELLOW}----------------------------------------------------------${NC}"
  echo -e "${CYAN}[INFO] Construction de l'image : ${full_tag} dans ${context} [${PLATFORM}]${NC}"
  
  start_time=$(date +%s)
  (
    cd "${target_dir}"
    docker buildx build --platform "${PLATFORM}" ${NO_CACHE} -t "${full_tag}" --load .
  )
  end_time=$(date +%s)
  duration=$((end_time - start_time))

  echo -e "${GREEN}[SUCCESS] Image ${full_tag} construite en ${duration}s.${NC}"

  # Injection automatique dans Kind pour accès Helm
  if [ -n "$KIND_CLUSTER" ]; then
    echo -e "${CYAN}[INFO] Injection dans le cluster Kind '${KIND_CLUSTER}' : ${full_tag}...${NC}"
    kind load docker-image "${full_tag}" --name "${KIND_CLUSTER}"
    echo -e "${GREEN}[SUCCESS] Image ${full_tag} injectée dans Kind avec succès.${NC}"
  fi
}

if [[ "$SERVICE" == "all" || "$SERVICE" == "payment-api" ]]; then
  build_image "payment-api" "services/payment-api"
fi

if [[ "$SERVICE" == "all" || "$SERVICE" == "remediation-engine" ]]; then
  build_image "remediation-engine" "services/remediation-engine"
fi

if [[ "$SERVICE" == "all" || "$SERVICE" == "auth-service" ]]; then
  build_image "auth-service" "services/auth-service"
fi

if [[ "$SERVICE" == "all" || "$SERVICE" == "dashboard-ui" ]]; then
  build_image "dashboard-ui" "services/dashboard-ui"
fi

if [[ "$SERVICE" == "all" || "$SERVICE" == "aiops-detector" ]]; then
  build_image "aiops-detector" "ai-ops/detector"
fi

echo -e "\n${GREEN}==========================================================${NC}"
echo -e "${GREEN}  BUILD TERMINÉ AVEC SUCCÈS !                             ${NC}"
echo -e "${GREEN}==========================================================${NC}"
docker images | grep -E "payment-api|remediation-engine|auth-service|dashboard-ui|aiops-detector" | grep "${TAG}" || true
