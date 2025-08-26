#!/bin/bash

# RunPod Deployment Script for Styled AI Service

echo "🚀 Deploying Styled AI to RunPod..."

# Configuration
REGISTRY="your-registry"  # Change this to your registry
IMAGE_NAME="styled-ai"
TAG="gpu-latest"
RUNPOD_API_KEY="your-runpod-api-key"  # Set this

# Build Docker image
echo "📦 Building Docker image..."
docker build -f Dockerfile -t $REGISTRY/$IMAGE_NAME:$TAG .

# Push to registry
echo "📤 Pushing to registry..."
docker push $REGISTRY/$IMAGE_NAME:$TAG

# Deploy to RunPod (if you have RunPod CLI)
if command -v runpod &> /dev/null; then
    echo "🚀 Deploying to RunPod..."
    runpod pod create \
        --name "styled-ai-service" \
        --image $REGISTRY/$IMAGE_NAME:$TAG \
        --gpu-count 1 \
        --cpu-count 4 \
        --memory 16 \
        --disk-size 50 \
        --env SECRET_KEY="your-secret-key" \
        --env GPU_ENABLED="true" \
        --env MODEL_PRECISION="float16" \
        --env BATCH_SIZE="8"
else
    echo "⚠️  RunPod CLI not found. Deploy manually using the web interface."
    echo "📋 Use the runpod-template.json configuration."
fi

echo "✅ Deployment script completed!"
echo "🔗 Check RunPod dashboard for pod status"
