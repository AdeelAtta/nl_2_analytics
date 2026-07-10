#!/usr/bin/env bash
set -euo pipefail

REGISTRY="${REGISTRY:-localhost:5000}"
TAG="${TAG:-latest}"

if [ "$REGISTRY" = "localhost:5000" ]; then
    echo "WARNING: Using default local registry $REGISTRY"
    echo "Set REGISTRY env var to push to a real registry."
fi

echo "Pushing backend image..."
docker push ${REGISTRY}/upl/backend:${TAG}

echo "Pushing frontend image..."
docker push ${REGISTRY}/upl/frontend:${TAG}

echo ""
echo "Images pushed successfully:"
echo "  ${REGISTRY}/upl/backend:${TAG}"
echo "  ${REGISTRY}/upl/frontend:${TAG}"
