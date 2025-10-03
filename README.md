# Azure AI Search RAG Application

A Python application that provides RAG (Retrieval-Augmented Generation) capabilities using Azure AI Search, Azure OpenAI, Azure Blob Storage, MongoDB, and Apify web scraping. Features multi-tenant architecture and comprehensive document processing.

## Features

- **Document Processing**: Supports PDF, DOCX, CSV, PPTX, XLSX, and TXT files
- **Web Scraping**: Automated website content extraction using Apify
- **Vector Search**: Azure AI Search with OpenAI embeddings for semantic search
- **RAG Pipeline**: Complete retrieval-augmented generation workflow
- **Multi-Tenant**: Organization-based document isolation
- **MongoDB Integration**: Metadata storage and tracking
- **Kubernetes Ready**: Docker and K8s deployment support

## Prerequisites

- Python 3.11+
- Docker
- Azure AI Search service
- Azure OpenAI service
- Azure Blob Storage account
- MongoDB instance (optional)
- Apify account for web scraping (optional)

## Environment Variables

Create a `.env` file with these variables:

```bash
# Required Azure Configuration
AZURE_SEARCH_SERVICE_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_ADMIN_KEY=your_search_admin_key_here
AZURE_OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com
AZURE_OPENAI_API_KEY=your_openai_api_key_here
AZURE_STORAGE_ACCOUNT_NAME=your_storage_account_name
AZURE_STORAGE_CONNECTION_STRING=your_storage_connection_string

# Organization Configuration
ORGANIZATION_ID=org_33EBz4so6OdUfUM2dPOveY3WRnF

# Optional Configuration
AZURE_SEARCH_INDEX_NAME=default
AZURE_OPENAI_CHAT_COMPLETION_DEPLOYED_MODEL_NAME=gpt-4
AZURE_OPENAI_EMBEDDING_DEPLOYED_MODEL_NAME=text-embedding-ada-002
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE_NAME=azure_rag_knowledge
WEBSITE_URL=https://example.com
APIFY_TOKEN=your_apify_token_here
LOG_LEVEL=INFO
```

## Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the application:**
```bash
# Main application with file processing
python main.py

# Interactive query mode
python query.py

# Test web scraping
python test_webscrap.py

# Usage examples
python usage.py
```

## Available Scripts

- `main.py` - Main application with file processing and optional web scraping
- `query.py` - Interactive query interface
- `test_webscrap.py` - Web scraping test
- `usage.py` - Usage examples and API demonstrations

## Docker Deployment

```bash
# Build the image
docker build -t azure-rag-app .

# Run the container
docker run -d --name azure-rag-app \
  -e AZURE_SEARCH_SERVICE_ENDPOINT="your_endpoint" \
  -e AZURE_SEARCH_ADMIN_KEY="your_key" \
  -e AZURE_OPENAI_ENDPOINT="your_endpoint" \
  -e AZURE_OPENAI_API_KEY="your_key" \
  -e AZURE_STORAGE_ACCOUNT_NAME="your_account" \
  -e AZURE_STORAGE_CONNECTION_STRING="your_connection" \
  azure-rag-app
```

## Kubernetes Deployment

1. **Update Configuration:**
   Edit `k8s-deployment.yaml` and replace placeholder values with your Azure credentials.

2. **Deploy:**
```bash
# Using the deployment script
scripts\deploy.bat  # Windows
./scripts/deploy.sh  # Linux/Mac

# Or manually
kubectl apply -f k8s-deployment.yaml
```

3. **Verify Deployment:**
```bash
kubectl get deployments
kubectl get pods
kubectl logs -f deployment/azure-rag-app
```

## Interacting with the Application

**Interactive Queries:**
```bash
# Access the running pod
kubectl exec -it <pod-name> -- python query.py

# Example queries:
# "What is the main topic of the documents?"
# "Summarize the key points from the uploaded files"
```

**Add Documents:**
```bash
# Copy documents to the pod
kubectl cp your-document.pdf <pod-name>:/app/data/

# Process documents
kubectl exec -it <pod-name> -- python main.py
```

## Architecture

The application processes documents through the following workflow:

1. **Document Upload**: Files are uploaded to Azure Blob Storage
2. **Text Extraction**: Content is extracted from various file formats
3. **Chunking**: Text is split into manageable chunks
4. **Embedding**: Chunks are converted to vector embeddings using Azure OpenAI
5. **Indexing**: Documents with embeddings are stored in Azure AI Search
6. **Query**: Users can query using semantic search and get RAG responses

## Project Structure

```
src/
├── clients.py              # Azure service clients
├── document_processor.py   # File processing and blob storage
├── web_scraper.py          # Web content extraction with Apify
├── search_index.py         # Azure AI Search index management
├── search.py               # Vector search and RAG responses
├── embeddings.py           # OpenAI embedding generation
├── chunking.py             # Text chunking algorithms
├── mongodb_service.py      # MongoDB metadata operations
├── file_processors.py     # Multi-format file processing
└── manage_org.py          # Organization management
```

## Troubleshooting

**Common Issues:**
- Verify Azure service endpoints and keys
- Check file format support
- Review application logs
- Validate MongoDB connection

**Debug Commands:**
```bash
# Check pod status
kubectl get pods -o wide

# View logs
kubectl logs -f deployment/azure-rag-app

# Describe pod for detailed info
kubectl describe pod <pod-name>
```
