# Azure AI Search RAG Application - Production Ready

A comprehensive, production-ready Python application that provides advanced RAG (Retrieval-Augmented Generation) capabilities using Azure AI Search, Azure OpenAI, Azure Blob Storage, MongoDB, and Apify web scraping. Features multi-tenant architecture, comprehensive document processing, and automated web content extraction.

## 🚀 Features

### Core RAG Capabilities
- **Document Processing**: Supports PDF, DOCX, CSV, PPTX, XLSX, and TXT files
- **Web Scraping**: Automated website content extraction using Apify
- **Vector Search**: Azure AI Search with OpenAI embeddings for semantic search
- **RAG Pipeline**: Complete retrieval-augmented generation workflow
- **Multi-Tenant**: Organization-based document isolation with separate indexes

### Infrastructure & Storage
- **Azure Blob Storage**: Automatic file upload and management
- **MongoDB Integration**: Comprehensive metadata storage and tracking
- **Azure AI Search**: Vector and semantic search capabilities
- **Azure OpenAI**: Embedding generation and chat completions

### Deployment & Operations
- **Kubernetes Ready**: Complete Docker and K8s deployment manifests
- **Production Features**: Health checks, resource limits, comprehensive logging
- **Container-Friendly**: Optimized for container deployment without interactive input
- **Scalable Architecture**: Horizontal scaling support

## 📋 Prerequisites

### System Requirements
- Python 3.11+
- Docker
- Kubernetes cluster (optional for local development)

### Azure Services
- Azure AI Search service
- Azure OpenAI service
- Azure Blob Storage account

### External Services (Optional)
- MongoDB instance (local or cloud)
- Apify account for web scraping

## ⚙️ Environment Variables

Copy `env.example` to `.env` and configure:

```bash
cp env.example .env
```

### Required Variables:
- `AZURE_SEARCH_SERVICE_ENDPOINT`: Azure Search service endpoint
- `AZURE_SEARCH_ADMIN_KEY`: Azure Search service admin key
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI endpoint
- `AZURE_OPENAI_API_KEY`: Azure OpenAI API key
- `AZURE_STORAGE_ACCOUNT_NAME`: Azure Storage account name
- `AZURE_STORAGE_CONNECTION_STRING`: Azure Storage connection string
- `ORGANIZATION_ID`: Organization identifier for multi-tenancy

### Optional Variables:
- `AZURE_SEARCH_INDEX_NAME`: Search index name (default: default)
- `AZURE_OPENAI_CHAT_COMPLETION_DEPLOYED_MODEL_NAME`: Chat model name (default: gpt-4)
- `AZURE_OPENAI_EMBEDDING_DEPLOYED_MODEL_NAME`: Embedding model name (default: text-embedding-ada-002)
- `MONGODB_URL`: MongoDB connection string (default: mongodb://localhost:27017)
- `MONGODB_DATABASE_NAME`: MongoDB database name (default: azure_rag_knowledge)
- `WEBSITE_URL`: Website URL to scrape (optional)
- `APIFY_TOKEN`: Apify API token for web scraping (required if using web scraping)
- `LOG_LEVEL`: Logging level (default: INFO)

## 🏠 Local Development

### Quick Start

1. **Clone and setup:**
```bash
git clone <repository-url>
cd AzureAi-search_RAG
cp env.example .env
# Edit .env with your Azure credentials
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
# Basic file processing
python main.py

# Test web scraping integration
python test_web_scraping.py

# Run comprehensive example
python rag_example.py

# Standalone web scraping
python scrape_website.py
```

4. **Interactive queries:**
```bash
python query.py
```

### Available Scripts

- `main.py` - Main application with file processing and optional web scraping
- `scrape_website.py` - Standalone web scraping tool
- `rag_example.py` - Comprehensive example with both file processing and web scraping
- `test_web_scraping.py` - Integration test for web scraping functionality
- `query.py` - Interactive query interface
- `usage.py` - Usage examples and API demonstrations

## 🐳 Docker Build

```bash
# Build the image
docker build -t azure-rag-app .

# Or use the build script
scripts\build.bat  # Windows
./scripts/build.sh  # Linux/Mac
```

## ☸️ Kubernetes Deployment

### 1. Build and Push Docker Image

```bash
# Build the image
docker build -t azure-rag-app:latest .

# Tag for your registry (optional)
docker tag azure-rag-app:latest your-registry/azure-rag-app:latest

# Push to registry (optional)
docker push your-registry/azure-rag-app:latest
```

### 2. Update Kubernetes Configuration

Edit `k8s-deployment.yaml`:
- Update the ConfigMap with your configuration
- Update the Secret with your actual Azure credentials
- Adjust resource limits if needed

### 3. Deploy to Kubernetes

```bash
# Deploy using the script
scripts\deploy.bat  # Windows
./scripts/deploy.sh  # Linux/Mac

# Or deploy manually
kubectl apply -f k8s-deployment.yaml
```

### 4. Verify Deployment

```bash
# Check deployment status
kubectl get deployments
kubectl get pods

# View logs
kubectl logs -f deployment/azure-rag-app
```

### 5. Run as a One-time Job

```bash
# Create a new job from the template
kubectl create job azure-rag-run --from=job/azure-rag-job

# Check job status
kubectl get jobs
kubectl logs -f job/azure-rag-run
```

## 📜 Using the Scripts

### Build Script
```bash
# Windows
scripts\build.bat
scripts\build.bat v1.0.0
scripts\build.bat latest your-registry.com

# Linux/Mac
./scripts/build.sh
./scripts/build.sh v1.0.0
./scripts/build.sh latest your-registry.com
```

### Deploy Script
```bash
# Windows
scripts\deploy.bat
scripts\deploy.bat production
scripts\deploy.bat default your-registry.com/azure-rag-app:v1.0.0

# Linux/Mac
./scripts/deploy.sh
./scripts/deploy.sh production
./scripts/deploy.sh default your-registry.com/azure-rag-app:v1.0.0
```

### Activation Script
```bash
# Windows
scripts\activate.bat

# Linux/Mac
source scripts/activate.sh
```

## 🏗️ Architecture

### System Overview
```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────────┐
│   Documents     │───▶│  File        │───▶│  Python App        │
│   (Blob Storage)│    │  Processing  │    │  (Kubernetes Pod)   │
└─────────────────┘    └──────────────┘    └─────────────────────┘
                                                      │
                                                      ▼
┌─────────────────┐    ┌──────────────┐    ┌─────────────────────┐
│ Azure AI        │◀───│ Azure OpenAI │◀───│  Chunking &         │
│ Search           │    │ Embeddings   │    │  Embedding          │
└─────────────────┘    └──────────────┘    └─────────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌──────────────┐    ┌─────────────────────┐
│ RAG Response    │◀───│ Vector       │◀───│  User Queries       │
│                 │    │ Search       │    │  (kubectl exec)     │
└─────────────────┘    └──────────────┘    └─────────────────────┘
```

### Enhanced Architecture with MongoDB and Web Scraping
```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────────┐
│   Web Sites     │───▶│  Apify       │───▶│  Web Scraper       │
│   (External)    │    │  Scraping    │    │  Module            │
└─────────────────┘    └──────────────┘    └─────────────────────┘
                                                      │
                                                      ▼
┌─────────────────┐    ┌──────────────┐    ┌─────────────────────┐
│   Documents     │───▶│  File        │───▶│  Document           │
│   (Blob Storage)│    │  Processing  │    │  Processor          │
└─────────────────┘    └──────────────┘    └─────────────────────┘
                                                      │
                                                      ▼
┌─────────────────┐    ┌──────────────┐    ┌─────────────────────┐
│   MongoDB       │◀───│  Metadata    │◀───│  Content            │
│   (Metadata)    │    │  Storage     │    │  Processing         │
└─────────────────┘    └──────────────┘    └─────────────────────┘
                                                      │
                                                      ▼
┌─────────────────┐    ┌──────────────┐    ┌─────────────────────┐
│ Azure AI        │◀───│ Azure OpenAI │◀───│  Embedding          │
│ Search           │    │ Embeddings   │    │  Generation         │
└─────────────────┘    └──────────────┘    └─────────────────────┘
```

### Component Details

**Core Modules:**
- `src/clients.py` - Azure service client management
- `src/document_processor.py` - File processing and blob storage
- `src/web_scraper.py` - Web content extraction with Apify
- `src/search_index.py` - Azure AI Search index management
- `src/search.py` - Vector search and RAG responses
- `src/embeddings.py` - OpenAI embedding generation
- `src/chunking.py` - Text chunking algorithms
- `src/mongodb_service.py` - MongoDB metadata operations
- `src/file_processors.py` - Multi-format file processing
- `src/manage_org.py` - Organization management

## 🔄 Application Workflow

### File Processing Workflow
1. **Document Upload**: Files are uploaded to organization-specific blob containers
2. **Text Extraction**: Content is extracted from various file formats (PDF, DOCX, CSV, PPTX, XLSX, TXT)
3. **Chunking**: Text is split into manageable chunks with configurable overlap
4. **Embedding**: Chunks are converted to vector embeddings using Azure OpenAI
5. **Indexing**: Documents with embeddings are stored in Azure AI Search
6. **Metadata Storage**: Document metadata is stored in MongoDB for tracking

### Web Scraping Workflow
1. **URL Processing**: Website URLs are processed using Apify web scraper
2. **Content Extraction**: Web pages are scraped with navigation/footer removal
3. **Multi-page Crawling**: Follows links up to 2 levels deep (configurable)
4. **Content Processing**: Scraped content follows the same chunking and embedding process
5. **Metadata Tracking**: Web scraping metadata is stored in MongoDB

### Query Processing Workflow
1. **Query Vectorization**: User queries are converted to embeddings
2. **Vector Search**: Similar content is retrieved from Azure AI Search
3. **Context Assembly**: Retrieved chunks are assembled with metadata
4. **RAG Response**: Context is used to generate responses via Azure OpenAI
5. **Organization Filtering**: Results are filtered by organization ID

## 📊 Monitoring

The application includes comprehensive logging:
- Application logs are written to stdout
- Structured logging with timestamps and log levels
- Error tracking with stack traces
- Performance metrics (processing time, document counts)

### View Logs
```bash
# View application logs
kubectl logs -f deployment/azure-rag-app

# View job logs
kubectl logs -f job/azure-rag-job

# View specific pod logs
kubectl logs -f <pod-name>
```

## 🔧 Troubleshooting

### Common Issues

1. **Image Pull Errors**
   - Ensure `imagePullPolicy: Never` for local images
   - Or push image to a registry and update `imagePullPolicy: Always`

2. **Missing Environment Variables**
   - Check that all required environment variables are set
   - Verify Azure service endpoints and keys

3. **Azure Service Connection Issues**
   - Verify Azure Search service is running
   - Check Azure OpenAI service availability
   - Validate Azure Storage account access

4. **Document Processing Failures**
   - Check file format support
   - Verify file permissions
   - Review extraction logs

5. **Kubernetes Deployment Issues**
   - Check pod logs: `kubectl logs <pod-name>`
   - Verify secrets and configmaps: `kubectl describe secret azure-rag-secrets`
   - Check resource limits and requests

### Debug Commands
```bash
# Check pod status
kubectl get pods -o wide

# Describe pod for detailed info
kubectl describe pod <pod-name>

# Check resource usage
kubectl top pods

# Check events
kubectl get events --sort-by=.metadata.creationTimestamp
```

## 🔒 Security Considerations

- Secrets are stored in Kubernetes secrets (not in the image)
- Non-root user in Docker container
- Resource limits to prevent resource exhaustion
- Network policies can be applied for additional security
- Organization-based data isolation
- Azure credentials are properly secured

## 📈 Scaling

For large document processing or multiple organizations:
- Increase resource limits in the deployment
- Consider running multiple jobs in parallel
- Monitor Azure AI Search service limits
- Implement rate limiting for OpenAI API calls

### Scale Deployment
```bash
# Scale the deployment
kubectl scale deployment azure-rag-app --replicas=3

# Check scaled pods
kubectl get pods
```

## 💰 Cost Optimization

- Use appropriate resource requests/limits
- Consider spot instances for non-critical jobs
- Monitor Azure AI Search and OpenAI usage
- Implement content deduplication if needed
- Use appropriate chunk sizes to balance quality and cost

## 🏢 Multi-Tenant Architecture

The application supports multiple organizations:
- Each organization has its own search index
- Documents are isolated by organization ID
- Blob storage uses organization-specific containers
- Search queries are filtered by organization

## 📁 File Format Support

- **PDF**: PyPDF2 for text extraction
- **DOCX**: python-docx for Word documents
- **CSV**: pandas for structured data
- **PPTX**: python-pptx for PowerPoint presentations
- **XLSX/XLS**: openpyxl for Excel files
- **TXT**: Direct text file reading

## ⚡ Performance Considerations

- Chunk size: 800 characters (configurable)
- Chunk overlap: 100 characters (configurable)
- Vector dimensions: 1536 (OpenAI standard)
- Batch processing for large document sets
- Async operations where possible

## 🌐 Web Scraping

The application includes comprehensive web scraping capabilities using Apify. This allows you to automatically extract content from websites and add it to your RAG system.

### Setup Web Scraping

1. **Get an Apify token:**
   - Sign up at [Apify.com](https://apify.com)
   - Get your API token from the account settings

2. **Configure environment variables:**
   ```bash
   WEBSITE_URL=https://example.com
   APIFY_TOKEN=your_apify_token_here
   ```

3. **Run web scraping:**
   ```bash
   # Standalone web scraping
   python scrape_website.py
   
   # Or run the comprehensive example
   python rag_example.py
   
   # Test integration
   python test_web_scraping.py
   ```

### Web Scraping Features

- **Automatic Content Extraction**: Removes navigation, headers, and footers
- **Multi-page Crawling**: Follows links up to 2 levels deep (configurable)
- **Content Chunking**: Automatically chunks content for optimal search
- **Metadata Preservation**: Maintains URL, title, and scraping metadata
- **Error Handling**: Graceful handling of scraping failures
- **Async Processing**: Efficient async/await implementation
- **MongoDB Integration**: Scraped content metadata stored in MongoDB

### Web Scraping Configuration

The web scraper can be configured with the following parameters:
- `maxCrawlDepth`: Maximum depth for following links (default: 2)
- `maxCrawlPages`: Maximum number of pages to crawl (default: 50)
- `chunk_size`: Size of content chunks (default: 800 characters)
- `overlap`: Overlap between chunks (default: 100 characters)

## 🎯 Usage Examples

### Basic Usage

```bash
# Process local files
python main.py

# Interactive query mode
python query.py

# Web scraping only
python scrape_website.py

# Comprehensive example (files + web scraping)
python rag_example.py

# Test web scraping integration
python test_web_scraping.py
```

### Interact with the Application
```bash
# Access the running pod
kubectl exec -it <pod-name> -- python query.py

# Add documents for processing
kubectl cp your-document.pdf <pod-name>:/app/data/

# Process documents
kubectl exec -it <pod-name> -- python main.py
```

### Query the RAG System
```bash
# Interactive query mode
kubectl exec -it <pod-name> -- python query.py

# Example queries:
# "What is the main topic of the documents?"
# "Summarize the key points from the uploaded files"
# "Find information about specific topics"
# "What content was scraped from the website?"
```

### API Usage Examples

```python
from src.search import search_documents
from src.document_processor import process_and_upload_org_files
from src.web_scraper import scrape_and_process_website_sync
from src.manage_org import create_org

# Create organization
org_id = "my-company"
result = create_org(org_id)

# Process files
process_and_upload_org_files(org_id, "./data")

# Scrape website
scrape_and_process_website_sync(org_id, "https://example.com")

# Query the system
response = search_documents(org_id, "What is the main topic?")
print(response)
```

## 🚀 Current Status

### ✅ Production Ready Features
- **Azure Integration**: All Azure services connected and working
- **Multi-Tenant**: Organization-based isolation implemented
- **Document Processing**: Support for PDF, DOCX, CSV, PPTX, XLSX, TXT
- **Web Scraping**: Automated content extraction with Apify
- **MongoDB Integration**: Comprehensive metadata storage
- **Vector Search**: Azure AI Search with semantic capabilities
- **RAG Pipeline**: Complete retrieval-augmented generation

### ✅ Deployment Ready
- **Kubernetes Ready**: Complete Docker and K8s deployment manifests
- **Production Features**: Health checks, resource limits, comprehensive logging
- **Container Optimized**: No interactive input dependencies
- **Scalable**: Ready for horizontal scaling
- **Security**: No hardcoded credentials, proper secret management

### ✅ Code Quality
- **Error Handling**: Comprehensive error handling throughout
- **Async Support**: Proper async/await implementation
- **Modular Design**: Clean, maintainable architecture
- **Testing**: Integration tests and validation scripts
- **Documentation**: Comprehensive README and code comments  

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review application logs: `kubectl logs -f deployment/azure-rag-app`
3. Verify Azure service connectivity
4. Check Kubernetes resource availability
5. Test web scraping integration: `python test_web_scraping.py`
6. Validate MongoDB connection and configuration

## 🔧 Troubleshooting

### Common Issues

1. **Image Pull Errors**
   - Ensure `imagePullPolicy: Never` for local images
   - Or push image to a registry and update `imagePullPolicy: Always`

2. **Missing Environment Variables**
   - Check that all required environment variables are set
   - Verify Azure service endpoints and keys
   - Ensure MongoDB connection string is correct

3. **Azure Service Connection Issues**
   - Verify Azure Search service is running
   - Check Azure OpenAI service availability
   - Validate Azure Storage account access

4. **Document Processing Failures**
   - Check file format support
   - Verify file permissions
   - Review extraction logs

5. **Web Scraping Issues**
   - Verify APIFY_TOKEN is set correctly
   - Check website accessibility
   - Review scraping logs for errors

6. **MongoDB Connection Issues**
   - Verify MongoDB URL and database name
   - Check MongoDB service availability
   - Review connection timeout settings

7. **Kubernetes Deployment Issues**
   - Check pod logs: `kubectl logs <pod-name>`
   - Verify secrets and configmaps: `kubectl describe secret azure-rag-secrets`
   - Check resource limits and requests

### Debug Commands
```bash
# Check pod status
kubectl get pods -o wide

# Describe pod for detailed info
kubectl describe pod <pod-name>

# Check resource usage
kubectl top pods

# Check events
kubectl get events --sort-by=.metadata.creationTimestamp

# Test web scraping integration
python test_web_scraping.py

# Check MongoDB connection
python -c "from src.mongodb_client import MongoDBClient; MongoDBClient()"
```

---

**🎉 Your Azure AI Search RAG application is now production-ready with comprehensive features:**

- ✅ **Multi-format document processing** (PDF, DOCX, CSV, PPTX, XLSX, TXT)
- ✅ **Automated web scraping** with Apify integration
- ✅ **Vector and semantic search** with Azure AI Search
- ✅ **MongoDB metadata tracking** for comprehensive data management
- ✅ **Multi-tenant architecture** with organization-based isolation
- ✅ **Production deployment** with Kubernetes and Docker
- ✅ **Comprehensive error handling** and monitoring
- ✅ **Scalable and secure** architecture

**Ready for enterprise deployment and production use!** 🚀