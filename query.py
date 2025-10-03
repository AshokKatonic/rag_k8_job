#!/usr/bin/env python3
"""
Interactive RAG Query Script
Use this script to interact with the RAG application
"""

from src.search import search_documents
import traceback

def query_rag():
    """
    Interactive query function for RAG application
    """
    test_org_id = "org_33EBz4so6OdUfUM2dPOveY3WRnF"
    
    print(f"Interactive RAG Query Mode for organization '{test_org_id}'")
    print("Enter your questions about the organization's documents (or 'exit' to quit):")
    
    while True:
        try:
            user_query = input(f"[{test_org_id}] Enter your question: ")
            if user_query.lower() == 'exit':
                break
            
            print(f"Processing query for organization '{test_org_id}': '{user_query}'")
            response = search_documents(test_org_id, user_query)
            
            print("\nAnswer:")
            print(response)
            print("\n------------------\n")
            
        except Exception as e:
            print(f"Error processing query: {e}")
            traceback.print_exc()
            print("Please try again or check your configuration.\n")

if __name__ == "__main__":
    query_rag()
