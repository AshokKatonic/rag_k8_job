@echo off
REM Build script for Azure RAG application (Windows)

setlocal enabledelayedexpansion

REM Configuration
set IMAGE_NAME=azure-rag-app
set TAG=%1
if "%TAG%"=="" set TAG=latest
set REGISTRY=%2

echo Building Docker image: %IMAGE_NAME%:%TAG%

REM Build the Docker image
docker build -t "%IMAGE_NAME%:%TAG%" .

if %ERRORLEVEL% neq 0 (
    echo Error building Docker image
    exit /b 1
)

echo Docker image built successfully: %IMAGE_NAME%:%TAG%

REM If registry is provided, tag and push
if not "%REGISTRY%"=="" (
    set FULL_IMAGE_NAME=%REGISTRY%/%IMAGE_NAME%:%TAG%
    echo Tagging image as: !FULL_IMAGE_NAME!
    docker tag "%IMAGE_NAME%:%TAG%" "!FULL_IMAGE_NAME!"
    
    echo Pushing image to registry...
    docker push "!FULL_IMAGE_NAME!"
    
    if %ERRORLEVEL% neq 0 (
        echo Error pushing image to registry
        exit /b 1
    )
    
    echo Image pushed successfully: !FULL_IMAGE_NAME!
)

echo Build completed successfully!
