"""
MongoDB service layer for CRUD operations on knowledge sources and documents
"""
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from bson import ObjectId
from .mongodb_client import (
    get_knowledge_sources_collection, 
    get_knowledge_documents_collection,
    KnowledgeSource,
    KnowledgeDocument
)


class KnowledgeSourceService:
    """Service for managing knowledge sources in MongoDB"""
    
    @staticmethod
    def create_knowledge_source(
        organization_id: str,
        name: str,
        description: Optional[str] = None,
        source_type: str = "DOCUMENT",
        configuration: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new knowledge source"""
        collection = get_knowledge_sources_collection()
        
        document = KnowledgeSource.create_document(
            organization_id=organization_id,
            name=name,
            description=description,
            source_type=source_type,
            configuration=configuration
        )
        
        result = collection.insert_one(document)
        print(f"Created knowledge source: {result.inserted_id}")
        return str(result.inserted_id)
    
    @staticmethod
    def get_knowledge_sources(organization_id: str) -> List[Dict[str, Any]]:
        """Get all knowledge sources for an organization"""
        collection = get_knowledge_sources_collection()
        
        cursor = collection.find(
            {"organizationId": organization_id}
        ).sort("createdAt", -1)
        
        sources = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
            sources.append(doc)
        
        return sources
    
    @staticmethod
    def get_knowledge_source(source_id: str, organization_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific knowledge source"""
        collection = get_knowledge_sources_collection()
        
        doc = collection.find_one({
            "_id": ObjectId(source_id),
            "organizationId": organization_id
        })
        
        if doc:
            doc["_id"] = str(doc["_id"])
        
        return doc
    
    @staticmethod
    def update_knowledge_source_status(
        source_id: str,
        status: str,
        organization_id: Optional[str] = None,
        error_message: Optional[str] = None,
        documents_processed: Optional[int] = None,
        documents_failed: Optional[int] = None
    ) -> bool:
        """Update knowledge source status"""
        collection = get_knowledge_sources_collection()
        
        updates = {
            "status": status,
            "updatedAt": datetime.utcnow()
        }
        
        if error_message is not None:
            updates["errorMessage"] = error_message
        
        if documents_processed is not None:
            updates["documentsProcessed"] = documents_processed
        
        if documents_failed is not None:
            updates["documentsFailed"] = documents_failed
        
        if status == "PROCESSING":
            updates["processStartedAt"] = datetime.utcnow()
        elif status == "COMPLETED":
            updates["lastProcessedAt"] = datetime.utcnow()
            updates["errorMessage"] = None
        
        filter_criteria = {"_id": ObjectId(source_id)}
        if organization_id:
            filter_criteria["organizationId"] = organization_id
        
        result = collection.update_one(filter_criteria, {"$set": updates})
        return result.modified_count > 0
    
    @staticmethod
    def delete_knowledge_source(source_id: str, organization_id: str) -> bool:
        """Delete a knowledge source and all its documents"""
        sources_collection = get_knowledge_sources_collection()
        documents_collection = get_knowledge_documents_collection()
        
        # Delete all documents first
        documents_result = documents_collection.delete_many({
            "knowledgeSourceId": ObjectId(source_id),
            "organizationId": organization_id
        })
        
        # Delete the knowledge source
        source_result = sources_collection.delete_one({
            "_id": ObjectId(source_id),
            "organizationId": organization_id
        })
        
        print(f"Deleted {documents_result.deleted_count} documents and 1 knowledge source")
        return source_result.deleted_count > 0
    
    @staticmethod
    def get_knowledge_source_stats(organization_id: str) -> Dict[str, int]:
        """Get statistics for knowledge sources"""
        collection = get_knowledge_sources_collection()
        
        pipeline = [
            {"$match": {"organizationId": organization_id}},
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }}
        ]
        
        stats = {"totalSources": 0, "completedSources": 0, "failedSources": 0, "processingSources": 0}
        
        for result in collection.aggregate(pipeline):
            status = result["_id"]
            count = result["count"]
            stats["totalSources"] += count
            
            if status == "COMPLETED":
                stats["completedSources"] = count
            elif status == "FAILED":
                stats["failedSources"] = count
            elif status == "PROCESSING":
                stats["processingSources"] = count
        
        return stats


class KnowledgeDocumentService:
    """Service for managing knowledge documents in MongoDB"""
    
    @staticmethod
    def create_document(
        knowledge_source_id: str,
        organization_id: str,
        title: str,
        content: str,
        url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a single knowledge document"""
        collection = get_knowledge_documents_collection()
        
        document = KnowledgeDocument.create_document(
            knowledge_source_id=knowledge_source_id,
            organization_id=organization_id,
            title=title,
            content=content,
            url=url,
            metadata=metadata
        )
        
        result = collection.insert_one(document)
        return str(result.inserted_id)
    
    @staticmethod
    def create_documents_batch(
        knowledge_source_id: str,
        organization_id: str,
        documents_data: List[Dict[str, Any]]
    ) -> List[str]:
        """Create multiple knowledge documents in a batch"""
        collection = get_knowledge_documents_collection()
        
        documents = KnowledgeDocument.create_batch_documents(
            knowledge_source_id=knowledge_source_id,
            organization_id=organization_id,
            documents_data=documents_data
        )
        
        result = collection.insert_many(documents)
        return [str(doc_id) for doc_id in result.inserted_ids]
    
    @staticmethod
    def get_documents_by_source(
        knowledge_source_id: str,
        organization_id: str
    ) -> List[Dict[str, Any]]:
        """Get all documents for a specific knowledge source"""
        collection = get_knowledge_documents_collection()
        
        cursor = collection.find({
            "knowledgeSourceId": ObjectId(knowledge_source_id),
            "organizationId": organization_id
        }).sort("createdAt", 1)
        
        documents = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            doc["knowledgeSourceId"] = str(doc["knowledgeSourceId"])
            documents.append(doc)
        
        return documents
    
    @staticmethod
    def get_documents_by_organization(organization_id: str) -> List[Dict[str, Any]]:
        """Get all documents for an organization"""
        collection = get_knowledge_documents_collection()
        
        cursor = collection.find(
            {"organizationId": organization_id}
        ).sort("createdAt", -1)
        
        documents = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            doc["knowledgeSourceId"] = str(doc["knowledgeSourceId"])
            documents.append(doc)
        
        return documents
    
    @staticmethod
    def get_document(document_id: str, organization_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document"""
        collection = get_knowledge_documents_collection()
        
        doc = collection.find_one({
            "_id": ObjectId(document_id),
            "organizationId": organization_id
        })
        
        if doc:
            doc["_id"] = str(doc["_id"])
            doc["knowledgeSourceId"] = str(doc["knowledgeSourceId"])
        
        return doc
    
    @staticmethod
    def update_document_status(
        document_id: str,
        status: str,
        organization_id: str,
        error_message: Optional[str] = None
    ) -> bool:
        """Update document processing status"""
        collection = get_knowledge_documents_collection()
        
        updates = {
            "status": status,
            "updatedAt": datetime.utcnow()
        }
        
        if status == "COMPLETED":
            updates["processedAt"] = datetime.utcnow()
            updates["errorMessage"] = None
        elif error_message:
            updates["errorMessage"] = error_message
        
        result = collection.update_one({
            "_id": ObjectId(document_id),
            "organizationId": organization_id
        }, {"$set": updates})
        
        return result.modified_count > 0
    
    @staticmethod
    def delete_document(document_id: str, organization_id: str) -> bool:
        """Delete a document"""
        collection = get_knowledge_documents_collection()
        
        result = collection.delete_one({
            "_id": ObjectId(document_id),
            "organizationId": organization_id
        })
        
        return result.deleted_count > 0
    
    @staticmethod
    def get_document_stats(organization_id: str) -> Dict[str, int]:
        """Get document statistics"""
        collection = get_knowledge_documents_collection()
        
        total_docs = collection.count_documents({"organizationId": organization_id})
        
        pipeline = [
            {"$match": {"organizationId": organization_id}},
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }}
        ]
        
        stats = {"totalDocuments": total_docs, "completedDocuments": 0, "failedDocuments": 0}
        
        for result in collection.aggregate(pipeline):
            status = result["_id"]
            count = result["count"]
            
            if status == "COMPLETED":
                stats["completedDocuments"] = count
            elif status == "FAILED":
                stats["failedDocuments"] = count
        
        return stats


class KnowledgeService:
    """Combined service for managing both knowledge sources and documents"""
    
    @staticmethod
    def process_file_batch(
        organization_id: str,
        source_name: str,
        file_data: List[Dict[str, Any]],
        description: Optional[str] = None,
        configuration: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, List[str]]:
        """Process a batch of files and store metadata in MongoDB"""
        
        # Create knowledge source
        source_id = KnowledgeSourceService.create_knowledge_source(
            organization_id=organization_id,
            name=source_name,
            description=description,
            source_type="DOCUMENT",
            configuration=configuration
        )
        
        # Update status to processing
        KnowledgeSourceService.update_knowledge_source_status(
            source_id=source_id,
            status="PROCESSING",
            organization_id=organization_id
        )
        
        try:
            # Create documents
            document_ids = KnowledgeDocumentService.create_documents_batch(
                knowledge_source_id=source_id,
                organization_id=organization_id,
                documents_data=file_data
            )
            
            # Update source status to completed
            KnowledgeSourceService.update_knowledge_source_status(
                source_id=source_id,
                status="COMPLETED",
                organization_id=organization_id,
                documents_processed=len(document_ids),
                documents_failed=0
            )
            
            print(f"Successfully processed {len(document_ids)} documents for source: {source_id}")
            return source_id, document_ids
            
        except Exception as e:
            # Update source status to failed
            KnowledgeSourceService.update_knowledge_source_status(
                source_id=source_id,
                status="FAILED",
                organization_id=organization_id,
                error_message=str(e),
                documents_processed=0,
                documents_failed=len(file_data)
            )
            raise
    
    @staticmethod
    def get_organization_stats(organization_id: str) -> Dict[str, Any]:
        """Get comprehensive stats for an organization"""
        source_stats = KnowledgeSourceService.get_knowledge_source_stats(organization_id)
        document_stats = KnowledgeDocumentService.get_document_stats(organization_id)
        
        return {
            **source_stats,
            **document_stats
        }
