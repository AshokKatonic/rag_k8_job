@echo off
setlocal enabledelayedexpansion

REM Load environment variables from .env file
if not exist .env (
    echo Error: .env file not found
    exit /b 1
)

REM Load .env file and set environment variables
for /f "usebackq tokens=1,2 delims==" %%a in (.env) do (
    if not "%%a"=="" if not "%%a:~0,1%"=="#" (
        set %%a=%%b
    )
)

REM Create the secret using kubectl
kubectl create secret generic azure-rag-secrets ^
    --from-literal=azure-search-service-endpoint="%AZURE_SEARCH_SERVICE_ENDPOINT%" ^
    --from-literal=azure-search-admin-key="%AZURE_SEARCH_ADMIN_KEY%" ^
    --from-literal=azure-openai-endpoint="%AZURE_OPENAI_ENDPOINT%" ^
    --from-literal=azure-openai-api-key="%AZURE_OPENAI_API_KEY%" ^
    --from-literal=azure-storage-account-name="%AZURE_STORAGE_ACCOUNT_NAME%" ^
    --from-literal=azure-storage-connection-string="%AZURE_STORAGE_CONNECTION_STRING%" ^
    --from-literal=mongodb-url="%MONGODB_URL%" ^
    --from-literal=mongodb-database-name="%MONGODB_DATABASE_NAME%" ^
    --from-literal=apify-token="%APIFY_TOKEN%" ^
    --dry-run=client -o yaml | kubectl apply -f -

if %errorlevel% equ 0 (
    echo Secrets created successfully!
) else (
    echo Failed to create secrets
    exit /b 1
)