#!/bin/bash

# Deployment script for Azure RAG Kubernetes job

set -e

# Configuration
NAMESPACE="${1:-default}"
IMAGE_NAME="${2:-azure-rag-app:latest}"

echo "Deploying Azure RAG application to namespace: ${NAMESPACE}"
echo "Using image: ${IMAGE_NAME}"

# Create namespace if it doesn't exist
kubectl create namespace "${NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -

# Update the image in the deployment file
sed "s|image: azure-rag-app:latest|image: ${IMAGE_NAME}|g" k8s-deployment.yaml > k8s-deployment-updated.yaml

# Apply the Kubernetes manifests
echo "Applying Kubernetes manifests..."
kubectl apply -f k8s-deployment-updated.yaml -n "${NAMESPACE}"

# Clean up temporary file
rm -f k8s-deployment-updated.yaml

echo "Deployment completed successfully!"
echo ""
echo "To check the status:"
echo "  kubectl get jobs -n ${NAMESPACE}"
echo "  kubectl get pods -n ${NAMESPACE}"
echo "  kubectl get deployments -n ${NAMESPACE}"
echo ""
echo "To view logs:"
echo "  kubectl logs -f job/azure-rag-job -n ${NAMESPACE}"
echo "  kubectl logs -f deployment/azure-rag-app -n ${NAMESPACE}"
echo ""
echo "To run a one-time job:"
echo "  kubectl create job azure-rag-run --from=job/azure-rag-job -n ${NAMESPACE}"
echo ""
echo "To interact with the application:"
echo "  kubectl exec -it deployment/azure-rag-app -n ${NAMESPACE} -- python main.py"
