#!/usr/bin/env bash
set -euo pipefail

REGISTRY="${REGISTRY:-}"
TAG="${TAG:-latest}"

echo "Building backend image..."
docker build \
    -t ${REGISTRY}upl/backend:${TAG} \
    -f infra/docker/Dockerfile.backend \
    --target prod \
    .

echo "Building frontend image..."
docker build \
    -t ${REGISTRY}upl/frontend:${TAG} \
    -f infra/docker/Dockerfile.frontend \
    --target prod \
    .

echo ""
echo "Images built successfully:"
echo "  ${REGISTRY}upl/backend:${TAG}"
echo "  ${REGISTRY}upl/frontend:${TAG}"
echo ""
echo "Set REGISTRY and TAG env vars to customize."
