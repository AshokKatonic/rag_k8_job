import os
from dotenv import load_dotenv

load_dotenv()

# Azure Search Configuration
AZURE_SEARCH_SERVICE_ENDPOINT = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
AZURE_SEARCH_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME")
AZURE_SEARCH_ADMIN_KEY = os.getenv("AZURE_SEARCH_ADMIN_KEY")


AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_CHAT_COMPLETION_DEPLOYED_MODEL_NAME = os.getenv("AZURE_OPENAI_CHAT_COMPLETION_DEPLOYED_MODEL_NAME")
AZURE_OPENAI_EMBEDDING_DEPLOYED_MODEL_NAME = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYED_MODEL_NAME")
AZURE_OPENAI_API_VERSION = "2024-02-01"

# Azure Blob Storage Configuration
AZURE_STORAGE_ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

# Organization-specific settings
DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 100

# Supported file extensions
SUPPORTED_EXTENSIONS = {'.txt', '.pdf', '.docx', '.csv', '.pptx', '.xlsx', '.xls'}

# Vector search configuration
VECTOR_SEARCH_DIMENSIONS = 1536
VECTOR_SEARCH_PROFILE_NAME = "my-vector-search-profile"
HNSW_CONFIG_NAME = "my-hnsw-config"
SEMANTIC_CONFIG_NAME = "my-semantic-config"

# HNSW parameters
HNSW_PARAMETERS = {
    "m": 4,
    "efConstruction": 400,
    "efSearch": 500,
    "metric": "cosine"
}

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL")
MONGODB_DATABASE_NAME = os.getenv("MONGODB_DATABASE_NAME", "azure_rag_knowledge")
MONGODB_COLLECTION_KNOWLEDGE_SOURCES = "knowledge_sources"
MONGODB_COLLECTION_KNOWLEDGE_DOCUMENTS = "knowledge_documents"