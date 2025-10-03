import os
import io
from datetime import datetime
from .clients import get_container_client, get_search_client
from .file_processors import (
    extract_text_from_file,
    extract_text_from_pdf,
    extract_text_from_docx,
    extract_text_from_csv,
    extract_text_from_pptx,
    extract_text_from_xlsx
)
from .chunking import chunk_text
from .embeddings import generate_embeddings
from .config import SUPPORTED_EXTENSIONS, DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP
from azure.core.exceptions import ResourceNotFoundError
from .clients import sanitize_azure_name
from .mongodb_service import KnowledgeService



def upload_file_to_org_blob(org_id, file_path, blob_name=None):
    """
    Uploads a file to the organization's blob container.
    
    Args:
        org_id (str): Organization identifier
        file_path (str): Local path to the file
        blob_name (str, optional): Name for the blob. If None, uses filename
        
    Returns:
        str: The blob name used for upload
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if blob_name is None:
        blob_name = os.path.basename(file_path)
    
    container_client = get_container_client(org_id)
    blob_client = container_client.get_blob_client(blob_name)
    
    with open(file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    
    print(f"Uploaded '{file_path}' as '{blob_name}' to organization '{org_id}' container")
    return blob_name


def download_file_from_org_blob(org_id, blob_name, local_path=None):
    """
    Downloads a file from the organization's blob container.
    
    Args:
        org_id (str): Organization identifier
        blob_name (str): Name of the blob to download
        local_path (str, optional): Local path to save the file
        
    Returns:
        str: The local path where the file was saved
    """
    if local_path is None:
        local_path = blob_name
    
    container_client = get_container_client(org_id)
    blob_client = container_client.get_blob_client(blob_name)
    
    with open(local_path, "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())
    
    print(f"Downloaded '{blob_name}' to '{local_path}' from organization '{org_id}'")
    return local_path


def extract_text_from_org_blob(org_id, blob_name):
    """
    Extracts text content from a blob in the organization's container.
    
    Args:
        org_id (str): Organization identifier
        blob_name (str): Name of the blob
        
    Returns:
        str: Extracted text content
    """
    container_client = get_container_client(org_id)
    blob_client = container_client.get_blob_client(blob_name)
    
    blob_data = blob_client.download_blob().readall()
    file_extension = os.path.splitext(blob_name)[1].lower()
    file_like = io.BytesIO(blob_data)
    
    try:
        if file_extension == '.txt':
            return file_like.read().decode('utf-8')
        elif file_extension == '.pdf':
            return extract_text_from_pdf(file_like)
        elif file_extension == '.docx':
            return extract_text_from_docx(file_like)
        elif file_extension == '.csv':
            return extract_text_from_csv(file_like)
        elif file_extension == '.pptx':
            return extract_text_from_pptx(file_like)
        elif file_extension in ['.xlsx', '.xls']:
            return extract_text_from_xlsx(file_like)
        else:
            print(f"Unsupported file format: {file_extension}")
            return ""
    except Exception as e:
        print(f"Error extracting text from blob '{blob_name}': {e}")
        return ""


def process_and_upload_org_files(org_id, directory_path, chunk_size=DEFAULT_CHUNK_SIZE, overlap=DEFAULT_CHUNK_OVERLAP):
    """
    Processes all supported files in a given directory for an organization,
    uploads them to blob storage, generates embeddings, uploads to search index,
    and stores metadata in MongoDB.
    
    Args:
        org_id (str): Organization identifier
        directory_path (str): Path to directory containing files
        chunk_size (int): Maximum size of each chunk in characters
        overlap (int): Number of characters to overlap between chunks
    """
    print(f"Processing files for organization '{org_id}' in directory: {directory_path}")
    print(f"Using chunk size: {chunk_size} characters, overlap: {overlap} characters")
    
    documents = []
    mongo_documents = []
    processed_files = 0
    
    org_search_client = get_search_client(org_id)
    
    # Create a knowledge source for this batch
    source_name = f"Batch Processing - {os.path.basename(directory_path)}"
    source_description = f"Files processed from directory: {directory_path}"
    
    try:
        for filename in os.listdir(directory_path):
            filepath = os.path.join(directory_path, filename)
            file_extension = os.path.splitext(filename)[1].lower()
            
            if os.path.isdir(filepath) or file_extension not in SUPPORTED_EXTENSIONS:
                continue
                
            print(f"Processing file: {filename} ({file_extension})")
            
            blob_name = upload_file_to_org_blob(org_id, filepath)
            
            content = extract_text_from_file(filepath)
            
            if not content.strip():
                print(f"Warning: No content extracted from {filename}")
                continue
                
            chunks = chunk_text(content, chunk_size, overlap)
            print(f"File '{filename}' split into {len(chunks)} chunks")
            
            safe_org_id = sanitize_azure_name(org_id)
            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    # Azure Search document
                    document = {
                        "id": f"{safe_org_id}_{filename.replace('.', '_')}_{i}",
                        "content": chunk,
                        "filepath": filename,
                        "organization_id": org_id,
                        "blob_name": blob_name,
                        "embedding": generate_embeddings(chunk)
                    }
                    documents.append(document)
                    
                    # MongoDB document metadata
                    mongo_doc = {
                        "title": f"{filename} - Chunk {i+1}",
                        "content": chunk,
                        "url": None,  # No URL for local files
                        "metadata": {
                            "filename": filename,
                            "filepath": filepath,
                            "blob_name": blob_name,
                            "chunk_index": i,
                            "total_chunks": len(chunks),
                            "file_extension": file_extension,
                            "processed_at": datetime.utcnow().isoformat(),
                            "source": "local_file",
                            "chunk_size": len(chunk),
                            "organization_id": org_id
                        }
                    }
                    mongo_documents.append(mongo_doc)
            
            processed_files += 1
        
        print(f"Processed {processed_files} files for organization '{org_id}'")
        
        # Upload to Azure Search
        if documents:
            try:
                org_search_client.merge_or_upload_documents(documents=documents)
                print(f"Uploaded {len(documents)} documents to organization '{org_id}' search index.")
            except AttributeError:
                try:
                    org_search_client.upload_documents(documents=documents, merge_mode="mergeOrUpload")
                    print(f"Uploaded {len(documents)} documents to organization '{org_id}' search index.")
                except TypeError:
                    print("Warning: Using basic upload - may create duplicates on re-runs")
                    org_search_client.upload_documents(documents=documents)
                    print(f"Uploaded {len(documents)} documents to organization '{org_id}' search index.")
        else:
            print("No new documents to upload to Azure Search.")
        
        # Store metadata in MongoDB
        if mongo_documents:
            try:
                configuration = {
                    "directory_path": directory_path,
                    "chunk_size": chunk_size,
                    "overlap": overlap,
                    "processed_files": processed_files,
                    "total_chunks": len(mongo_documents),
                    "processing_type": "batch_directory"
                }
                
                source_id, document_ids = KnowledgeService.process_file_batch(
                    organization_id=org_id,
                    source_name=source_name,
                    description=source_description,
                    file_data=mongo_documents,
                    configuration=configuration
                )
                
                print(f"Stored metadata for {len(document_ids)} documents in MongoDB")
                print(f"Knowledge source ID: {source_id}")
                
            except Exception as e:
                print(f"Error storing metadata in MongoDB: {e}")
                print("Azure Search documents uploaded successfully, but MongoDB storage failed")
        else:
            print("No documents to store in MongoDB.")
            
    except Exception as e:
        print(f"Error during file processing: {e}")
        raise


def list_org_blobs(org_id):
    """
    Lists all blobs in the organization's container.
    
    Args:
        org_id (str): Organization identifier
        
    Returns:
        list: List of blob names
    """
    container_client = get_container_client(org_id)
    blob_list = container_client.list_blobs()
    return [blob.name for blob in blob_list]


def delete_org_blob(org_id, blob_name):
    """
    Deletes a blob from the organization's container.
    
    Args:
        org_id (str): Organization identifier
        blob_name (str): Name of the blob to delete
    """
    container_client = get_container_client(org_id)
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.delete_blob()
    print(f"Deleted blob '{blob_name}' from organization '{org_id}'")