"""
MongoDB client and connection management for Azure RAG system
"""
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from .config import MONGODB_URL, MONGODB_DATABASE_NAME


class MongoDBClient:
    """MongoDB client singleton for managing connections"""
    
    _instance = None
    _client = None
    _database = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBClient, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self._connect()
    
    def _connect(self):
        """Establish MongoDB connection"""
        if not MONGODB_URL:
            raise ValueError("MONGODB_URL environment variable is required")
        
        try:
            self._client = MongoClient(
                MONGODB_URL,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=10000,  # 10 second timeout
                socketTimeoutMS=20000,  # 20 second timeout
            )
            self._database = self._client[MONGODB_DATABASE_NAME]
            
            # Test the connection
            self._client.admin.command('ping')
            print(f"Successfully connected to MongoDB database: {MONGODB_DATABASE_NAME}")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"Failed to connect to MongoDB: {e}")
            raise
    
    @property
    def database(self) -> Database:
        """Get the database instance"""
        if self._database is None:
            self._connect()
        return self._database
    
    @property
    def client(self) -> MongoClient:
        """Get the MongoDB client"""
        if self._client is None:
            self._connect()
        return self._client
    
    def close(self):
        """Close the MongoDB connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None


# Global MongoDB client instance
mongodb_client = MongoDBClient()


def get_knowledge_sources_collection() -> Collection:
    """Get the knowledge sources collection"""
    return mongodb_client.database["knowledge_sources"]


def get_knowledge_documents_collection() -> Collection:
    """Get the knowledge documents collection"""
    return mongodb_client.database["knowledge_documents"]


# MongoDB Document Models (Python dictionaries following the same schema as Eshal UI)

class KnowledgeSource:
    """Knowledge Source document model"""
    
    @staticmethod
    def create_document(
        organization_id: str,
        name: str,
        description: Optional[str] = None,
        source_type: str = "DOCUMENT",
        status: str = "PENDING",
        configuration: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a knowledge source document"""
        now = datetime.utcnow()
        
        return {
            "createdAt": now,
            "updatedAt": now,
            "organizationId": organization_id,
            "name": name,
            "description": description,
            "type": source_type,
            "status": status,
            "configuration": configuration or {},
            "lastProcessedAt": None,
            "processStartedAt": None,
            "errorMessage": None,
            "retryCount": 0,
            "documentsProcessed": 0,
            "documentsFailed": 0,
            **kwargs
        }
    
    @staticmethod
    def update_document(
        document_id: str,
        updates: Dict[str, Any],
        organization_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update a knowledge source document"""
        update_data = {
            "updatedAt": datetime.utcnow(),
            **updates
        }
        
        filter_criteria = {"_id": document_id}
        if organization_id:
            filter_criteria["organizationId"] = organization_id
        
        return get_knowledge_sources_collection().update_one(
            filter_criteria,
            {"$set": update_data}
        )


class KnowledgeDocument:
    """Knowledge Document model"""
    
    @staticmethod
    def create_document(
        knowledge_source_id: str,
        organization_id: str,
        title: str,
        content: str,
        url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        status: str = "COMPLETED",
        **kwargs
    ) -> Dict[str, Any]:
        """Create a knowledge document"""
        now = datetime.utcnow()
        
        return {
            "createdAt": now,
            "updatedAt": now,
            "knowledgeSourceId": knowledge_source_id,
            "organizationId": organization_id,
            "title": title,
            "content": content,
            "url": url,
            "metadata": metadata or {},
            "status": status,
            "processedAt": now if status == "COMPLETED" else None,
            "errorMessage": None,
            **kwargs
        }
    
    @staticmethod
    def create_batch_documents(
        knowledge_source_id: str,
        organization_id: str,
        documents_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Create multiple knowledge documents"""
        return [
            KnowledgeDocument.create_document(
                knowledge_source_id=knowledge_source_id,
                organization_id=organization_id,
                title=doc.get("title", "Untitled Document"),
                content=doc.get("content", ""),
                url=doc.get("url"),
                metadata=doc.get("metadata", {}),
                status=doc.get("status", "COMPLETED")
            )
            for doc in documents_data
        ]
