#!/bin/bash

# Build script for Azure RAG application

set -e

# Configuration
IMAGE_NAME="azure-rag-app"
TAG="${1:-latest}"
REGISTRY="${2:-}"

echo "Building Docker image: ${IMAGE_NAME}:${TAG}"

# Build the Docker image
docker build -t "${IMAGE_NAME}:${TAG}" .

echo "Docker image built successfully: ${IMAGE_NAME}:${TAG}"

# If registry is provided, tag and push
if [ -n "$REGISTRY" ]; then
    FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}:${TAG}"
    echo "Tagging image as: ${FULL_IMAGE_NAME}"
    docker tag "${IMAGE_NAME}:${TAG}" "${FULL_IMAGE_NAME}"
    
    echo "Pushing image to registry..."
    docker push "${FULL_IMAGE_NAME}"
    
    echo "Image pushed successfully: ${FULL_IMAGE_NAME}"
fi

echo "Build completed successfully!"
