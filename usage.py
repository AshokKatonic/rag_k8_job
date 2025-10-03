#!/usr/bin/env python3
"""
Simple RAG Wrapper - Complete Azure AI Search RAG System
A single-file wrapper for all RAG functionality with simple function calls
"""

import os
import sys
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Core imports
from src.search_index import create_search_index, delete_search_index
from src.document_processor import process_and_upload_org_files
from src.web_scraper import scrape_and_process_website_sync
from src.search import search_documents, perform_vector_search
from src.manage_org import create_org, delete_org, list_orgs, get_org_info
from src.config import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP
from src.mongodb_service import KnowledgeService


def setup_rag_system(org_id: str, data_directory: str = "./data", 
                     website_url: Optional[str] = None, 
                     chunk_size: int = DEFAULT_CHUNK_SIZE,
                     overlap: int = DEFAULT_CHUNK_OVERLAP) -> Dict[str, Any]:
    """
    Complete RAG system setup - processes files and optionally scrapes websites
    """
    print(f"Setting up RAG system for organization: {org_id}")
    
    try:
        # Step 1: Create organization
        print("Step 1: Creating organization...")
        result = create_org(org_id)
        print(f"Organization created: {result}")
        
        # Step 2: Process local files
        print("Step 2: Processing local files...")
        
        if not os.path.exists(data_directory):
            os.makedirs(data_directory)
            print(f"Created data directory: {data_directory}")
            
            sample_files = {
                "sample.txt": "Azure AI Search is a fully managed search-as-a-service. It provides a rich search experience to custom applications.\n\nRetrieval-Augmented Generation (RAG) is an AI framework for improving the quality of LLM-generated responses. It grounds the model on external sources of knowledge to supplement the LLM's internal representation of information.",
                "sample_data.txt": "Sample Data for Multi-Format RAG Testing\n\nThis document contains sample data to test the multi-format file processing capabilities of the Azure RAG implementation.\n\nKey Features:\n- PDF text extraction\n- DOCX document processing\n- CSV data parsing\n- PPTX presentation content extraction\n- XLSX spreadsheet processing\n\nThe system now supports comprehensive document ingestion for enterprise knowledge bases.",
                "sample.csv": "Name,Age,Department,Salary\nJohn Doe,30,Engineering,75000\nJane Smith,28,Marketing,65000\nBob Johnson,35,Sales,70000\nAlice Brown,32,Engineering,80000\nCharlie Wilson,29,Marketing,60000"
            }
            
            for filename, content in sample_files.items():
                filepath = os.path.join(data_directory, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Created sample file: {filename}")
        
        process_and_upload_org_files(
            org_id=org_id,
            directory_path=data_directory,
            chunk_size=chunk_size,
            overlap=overlap
        )
        print("Local files processed successfully!")
        
        # Step 3: Web scraping (optional)
        if website_url:
            print(f"Step 3: Scraping website: {website_url}")
            try:
                scrape_and_process_website_sync(
                    org_id=org_id,
                    url=website_url,
                    chunk_size=chunk_size,
                    overlap=overlap
                )
                print("Website scraping completed!")
            except Exception as e:
                print(f"Website scraping failed: {e}")
                print("Continuing with file-based RAG...")
        else:
            print("No website URL provided. Skipping web scraping.")
        
        # Step 4: Get system stats
        print("Step 4: Getting system statistics...")
        try:
            stats = KnowledgeService.get_organization_stats(org_id)
            print(f"System stats: {stats}")
        except Exception as e:
            print(f"Could not get stats: {e}")
            stats = {"status": "unknown"}
        
        return {
            "status": "success",
            "org_id": org_id,
            "message": "RAG system setup completed successfully",
            "stats": stats,
            "files_processed": True,
            "web_scraping": website_url is not None
        }
        
    except Exception as e:
        print(f"RAG system setup failed: {e}")
        return {
            "status": "error",
            "org_id": org_id,
            "message": f"Setup failed: {str(e)}",
            "error": str(e)
        }


def ask_question(org_id: str, question: str, max_results: int = 3) -> Dict[str, Any]:
    """
    Ask a question to the RAG system
    """
    print(f"Processing question for {org_id}: '{question}'")
    
    try:
        search_results = perform_vector_search(org_id, question, k=max_results)
        response = search_documents(org_id, question)
        
        return {
            "status": "success",
            "org_id": org_id,
            "question": question,
            "answer": response,
            "search_results_count": len(search_results),
            "search_results": search_results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error processing question: {e}")
        return {
            "status": "error",
            org_id: org_id,
            "question": question,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


def add_documents(org_id: str, file_paths: List[str], 
                  chunk_size: int = DEFAULT_CHUNK_SIZE,
                  overlap: int = DEFAULT_CHUNK_OVERLAP) -> Dict[str, Any]:
    """
    Add documents to the RAG system
    """
    print(f"Adding {len(file_paths)} documents to {org_id}")
    
    try:
        results = []
        for file_path in file_paths:
            if os.path.exists(file_path):
                from src.document_processor import upload_file_to_org_blob
                blob_name = upload_file_to_org_blob(org_id, file_path)
                
                process_and_upload_org_files(
                    org_id=org_id,
                    directory_path=os.path.dirname(file_path),
                    chunk_size=chunk_size,
                    overlap=overlap
                )
                
                results.append({
                    "file_path": file_path,
                    "blob_name": blob_name,
                    "status": "success"
                })
                print(f"Processed: {file_path}")
            else:
                results.append({
                    "file_path": file_path,
                    "status": "error",
                    "error": "File not found"
                })
                print(f"File not found: {file_path}")
        
        return {
            "status": "success",
            "org_id": org_id,
            "processed_files": results,
            "total_files": len(file_paths),
            "successful_files": len([r for r in results if r["status"] == "success"])
        }
        
    except Exception as e:
        print(f"Error adding documents: {e}")
        return {
            "status": "error",
            "org_id": org_id,
            "error": str(e)
        }


def scrape_website(org_id: str, website_url: str,
                   chunk_size: int = DEFAULT_CHUNK_SIZE,
                   overlap: int = DEFAULT_CHUNK_OVERLAP) -> Dict[str, Any]:
    """
    Scrape a website and add content to RAG system
    """
    print(f"Scraping website for {org_id}: {website_url}")
    
    try:
        scrape_and_process_website_sync(
            org_id=org_id,
            url=website_url,
            chunk_size=chunk_size,
            overlap=overlap
        )
        
        return {
            "status": "success",
            "org_id": org_id,
            "website_url": website_url,
            "message": "Website scraping completed successfully"
        }
        
    except Exception as e:
        print(f"Error scraping website: {e}")
        return {
            "status": "error",
            "org_id": org_id,
            "website_url": website_url,
            "error": str(e)
        }


def get_system_info(org_id: str) -> Dict[str, Any]:
    """
    Get information about the RAG system
    """
    print(f"Getting system info for {org_id}")
    
    try:
        org_info = get_org_info(org_id)
        stats = KnowledgeService.get_organization_stats(org_id)
        
        from src.document_processor import list_org_blobs
        blobs = list_org_blobs(org_id)
        
        return {
            "status": "success",
            "org_id": org_id,
            "organization_info": org_info,
            "mongodb_stats": stats,
            "blob_count": len(blobs),
            "blobs": blobs[:10],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error getting system info: {e}")
        return {
            "status": "error",
            "org_id": org_id,
            "error": str(e)
        }


def interactive_chat(org_id: str):
    """
    Start interactive chat session with RAG system
    """
    print(f"Starting interactive chat for organization: {org_id}")
    print("Type 'exit' to quit, 'help' for commands")
    
    while True:
        try:
            question = input(f"\n[{org_id}] Ask a question: ").strip()
            
            if question.lower() == 'exit':
                print("Goodbye!")
                break
            elif question.lower() == 'help':
                print("""
Available commands:
- Ask any question about your documents
- 'exit' - Quit the chat
- 'help' - Show this help
- 'stats' - Show system statistics
                """)
                continue
            elif question.lower() == 'stats':
                info = get_system_info(org_id)
                print(f"System Stats: {info}")
                continue
            elif not question:
                continue
            
            result = ask_question(org_id, question)
            
            if result["status"] == "success":
                print(f"\nAnswer:\n{result['answer']}")
                print(f"\nFound {result['search_results_count']} relevant documents")
            else:
                print(f"Error: {result['error']}")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")


def main():
    """
    Main function demonstrating RAG wrapper usage
    """
    print("Azure AI Search RAG Wrapper Demo")
    print("=" * 50)
    
    org_id = "demo_org_123"
    data_dir = "./data"
    website_url = os.getenv('WEBSITE_URL')
    
    print("\nSetting up RAG system...")
    setup_result = setup_rag_system(
        org_id=org_id,
        data_directory=data_dir,
        website_url=website_url
    )
    
    if setup_result["status"] != "success":
        print(f"Setup failed: {setup_result['error']}")
        return
    
    print("RAG system ready!")
    
    print("\nTesting with sample questions...")
    
    sample_questions = [
        "What is the main topic of the documents?",
        "Summarize the key information",
        "What are the important points?"
    ]
    
    for question in sample_questions:
        result = ask_question(org_id, question)
        if result["status"] == "success":
            print(f"\nQ: {question}")
            print(f"A: {result['answer'][:200]}...")
        else:
            print(f"Error with question '{question}': {result['error']}")
    
    print("\nStarting interactive chat...")
    interactive_chat(org_id)


if __name__ == "__main__":
    main()
