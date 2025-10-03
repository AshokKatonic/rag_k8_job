@echo off
REM Deployment script for Azure RAG Kubernetes job (Windows)

setlocal enabledelayedexpansion

REM Configuration
set NAMESPACE=%1
if "%NAMESPACE%"=="" set NAMESPACE=default
set IMAGE_NAME=%2
if "%IMAGE_NAME%"=="" set IMAGE_NAME=azure-rag-app:latest

echo Deploying Azure RAG application to namespace: %NAMESPACE%
echo Using image: %IMAGE_NAME%

REM Create namespace if it doesn't exist
kubectl create namespace "%NAMESPACE%" --dry-run=client -o yaml | kubectl apply -f -

REM Update the image in the deployment file
powershell -Command "(Get-Content k8s-deployment.yaml) -replace 'image: azure-rag-app:latest', 'image: %IMAGE_NAME%' | Set-Content k8s-deployment-updated.yaml"

REM Apply the Kubernetes manifests
echo Applying Kubernetes manifests...
kubectl apply -f k8s-deployment-updated.yaml -n "%NAMESPACE%"

if %ERRORLEVEL% neq 0 (
    echo Error applying Kubernetes manifests
    exit /b 1
)

REM Clean up temporary file
del k8s-deployment-updated.yaml

echo Deployment completed successfully!
echo.
echo To check the status:
echo   kubectl get jobs -n %NAMESPACE%
echo   kubectl get pods -n %NAMESPACE%
echo   kubectl get deployments -n %NAMESPACE%
echo.
echo To view logs:
echo   kubectl logs -f job/azure-rag-job -n %NAMESPACE%
echo   kubectl logs -f deployment/azure-rag-app -n %NAMESPACE%
echo.
echo To run a one-time job:
echo   kubectl create job azure-rag-run --from=job/azure-rag-job -n %NAMESPACE%
echo.
echo To interact with the application:
echo   kubectl exec -it deployment/azure-rag-app -n %NAMESPACE% -- python main.py
