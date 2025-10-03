from src.search_index import create_search_index, delete_search_index
from src.document_processor import process_and_upload_org_files
from src.web_scraper import scrape_and_process_website_sync
from src.search import search_documents
from src.manage_org import create_org, delete_org, list_orgs, get_org_info
from src.config import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP
import traceback
import os


def main():
    """
    Main application function for organization-based RAG workflow.
    """
    print("Starting Organization-based RAG application...")

    # Initialize organization manager
    # org_manager = OrganizationManager()
    
    try:
        test_org_id = "org_33EBz4so6OdUfUM2dPOveY3WRnF"
        
        print(f"Setting up organization: {test_org_id}")
        
        result = create_org(test_org_id)
        print(f"Organization creation result: {result}")
        
        # Process local files
        data_directory = "data"
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
            test_org_id, 
            data_directory, 
            chunk_size=DEFAULT_CHUNK_SIZE, 
            overlap=DEFAULT_CHUNK_OVERLAP
        )
        
        # Web scraping functionality
        website_url = os.getenv('WEBSITE_URL')
        if website_url:
            print(f"\nStarting web scraping from: {website_url}")
            try:
                scrape_and_process_website_sync(
                    test_org_id,
                    website_url,
                    chunk_size=DEFAULT_CHUNK_SIZE,
                    overlap=DEFAULT_CHUNK_OVERLAP
                )
                print("Web scraping completed successfully!")
            except Exception as e:
                print(f"Web scraping failed: {e}")
                print("Continuing with file-based RAG functionality...")
        else:
            print("No WEBSITE_URL environment variable set. Skipping web scraping.")
        
        print(f"\nRAG application setup completed for organization '{test_org_id}'")
        print("Application is ready for queries via kubectl exec or API calls")
        
        # For container deployment, we'll keep the application running
        # but not in interactive mode. Users can interact via kubectl exec
        print("To interact with the application, use:")
        print("kubectl exec -it <pod-name> -- python main.py")
        
        # Keep the container running
        import time
        while True:
            time.sleep(30)
            print("RAG application is running...")
            
    except Exception as e:
        print(f"Fatal error during initialization: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()