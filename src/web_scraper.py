"""
Web scraping utilities using Apify Cheerio Scraper
Handles website scraping and integration with Azure AI Search RAG
Uses Cheerio for efficient server-side HTML parsing
"""

import os
import logging
from typing import List, Dict, Any
from datetime import datetime
import asyncio

import apify_client as apify

from .clients import get_search_client, sanitize_azure_name
from .chunking import chunk_text
from .embeddings import generate_embeddings
from .config import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP
from .mongodb_service import KnowledgeService

logger = logging.getLogger(__name__)

def get_apify_client():
    """Get Apify client instance"""
    apify_token = os.getenv('APIFY_TOKEN')
    if not apify_token:
        raise ValueError("APIFY_TOKEN environment variable is required")
    
    return apify.ApifyClientAsync(token=apify_token)

async def scrape_website(url: str) -> List[Dict[str, Any]]:
    """Scrape website content using Apify Cheerio Scraper"""
    try:
        logger.info("Starting to scrape website: %s", url)
        
        # Get Apify client
        client = get_apify_client()
        
        # Use Apify's Cheerio Scraper with enhanced configuration
        run_input = {
            "startUrls": [{"url": url}],
            "maxCrawlDepth": 1,  # Limit depth for focused scraping
            "maxCrawlPages": 10,  # Limit pages to avoid overwhelming
            "pageFunction": """
                async ({ $, request, session, helpers, logins, Apify }) => {
                    try {
                        // Enhanced content extraction using Cheerio
                        
                        // Remove unwanted elements more comprehensively
                        const unwantedSelectors = [
                            'nav', 'header', 'footer', 'aside', 
                            '.navigation', '.nav', '.menu', '.sidebar',
                            '.footer', '.header', '.advertisement', '.ads',
                            'script', 'style', '.cookie-banner', '.popup', '.modal',
                            '.social-media', '.social-links', '.share-buttons',
                            '.comments', '.comment-section', '.related-posts',
                            '.breadcrumb', '.breadcrumbs', '.pagination',
                            '.newsletter', '.subscribe', '.signup'
                        ];
                        
                        unwantedSelectors.forEach(selector => {
                            $(selector).remove();
                        });
                        
                        // Extract title with fallbacks
                        let title = $('title').text().trim() || 
                                   $('h1').first().text().trim() || 
                                   $('meta[property="og:title"]').attr('content') ||
                                   'No Title';
                        
                        // Extract main content with better logic
                        let content = '';
                        
                        // Try to find main content areas first
                        const mainContentSelectors = [
                            'main', 'article', '.content', '.main-content',
                            '.post-content', '.entry-content', '.article-content',
                            '[role="main"]', '.page-content'
                        ];
                        
                        for (const selector of mainContentSelectors) {
                            const mainContent = $(selector).text().trim();
                            if (mainContent && mainContent.length > 100) {
                                content = mainContent;
                                break;
                            }
                        }
                        
                        // Fallback to body content if no main content found
                        if (!content) {
                            content = $('body').text().trim() || $('html').text().trim() || 'No Content';
                        }
                        
                        // Clean up content - remove extra whitespace and normalize
                        content = content.replace(/\\s+/g, ' ').trim();
                        
                        // Check for anti-bot measures
                        const bodyText = content.toLowerCase();
                        const isBlocked = bodyText.includes('access denied') || 
                            bodyText.includes('blocked') || 
                            bodyText.includes('bot detection') ||
                            bodyText.includes('please verify you are human') ||
                            bodyText.includes('cloudflare') ||
                            bodyText.includes('captcha');
                        
                        if (isBlocked) {
                            return {
                                url: request?.url || 'unknown',
                                title: 'Blocked',
                                content: 'Error scraping page: Page blocked by anti-bot measures',
                                metadata: {
                                    error: 'Anti-bot protection detected',
                                    timestamp: new Date().toISOString(),
                                    crawledAt: new Date().toISOString()
                                }
                            };
                        }
                        
                        // Extract additional metadata
                        const description = $('meta[name="description"]').attr('content') || 
                                         $('meta[property="og:description"]').attr('content') || '';
                        
                        const keywords = $('meta[name="keywords"]').attr('content') || '';
                        
                        return {
                            url: request?.url || 'unknown',
                            title: title,
                            content: content,
                            description: description,
                            keywords: keywords,
                            metadata: {
                                userAgent: request?.userData?.userAgent || 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                                timestamp: new Date().toISOString(),
                                crawledAt: new Date().toISOString(),
                                contentLength: content.length,
                                hasDescription: !!description,
                                hasKeywords: !!keywords
                            }
                        };
                    } catch (error) {
                        return {
                            url: request?.url || 'unknown',
                            title: 'Error',
                            content: `Error scraping page: ${error.message}`,
                            metadata: {
                                error: error.message,
                                timestamp: new Date().toISOString(),
                                crawledAt: new Date().toISOString()
                            }
                        };
                    }
                }
            """,
            "proxyConfiguration": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"]
            },
            "requestQueueId": None,  # Use default queue
            "maxRequestRetries": 3,
            "requestTimeoutSecs": 30
        }
        
        # Run the Cheerio scraper actor
        run = await client.actor("apify/cheerio-scraper").call(run_input=run_input)
        
        # Validate run result
        if not run or "defaultDatasetId" not in run:
            logger.error("Apify run failed or missing defaultDatasetId")
            raise ValueError("Failed to get dataset ID from Apify run")
        
        # Get the results
        dataset_response = await client.dataset(run["defaultDatasetId"]).list_items()
        
        scraped_content = []
        # Handle the ListPage object properly
        items = dataset_response.items if hasattr(dataset_response, 'items') else dataset_response
        
        if not items:
            logger.warning("No items found in Apify dataset response")
            return scraped_content
        
        for item in items:
            # Skip items with error content
            if item.get('content', '').startswith('Error scraping page:'):
                logger.warning(f"Skipping error item: {item.get('url', 'unknown')}")
                continue
                
            content = {
                'url': item.get('url', ''),
                'title': item.get('title', ''),
                'content': item.get('content', ''),
                'metadata': item.get('metadata', {}),
                'timestamp': datetime.now().isoformat()
            }
            scraped_content.append(content)
        
        logger.info("Successfully scraped %d pages from %s", len(scraped_content), url)
        return scraped_content
        
    except Exception as e:
        logger.error("Failed to scrape website %s: %s", url, e)
        raise

async def process_and_upload_scraped_content(org_id: str, scraped_content: List[Dict[str, Any]], 
                                     chunk_size: int = DEFAULT_CHUNK_SIZE, 
                                     overlap: int = DEFAULT_CHUNK_OVERLAP):
    """
    Process scraped website content and upload to Azure AI Search and MongoDB
    
    Args:
        org_id (str): Organization identifier
        scraped_content (List[Dict[str, Any]]): Scraped content from websites
        chunk_size (int): Maximum size of each chunk in characters
        overlap (int): Number of characters to overlap between chunks
    """
    print(f"Processing scraped content for organization '{org_id}'")
    print(f"Using chunk size: {chunk_size} characters, overlap: {overlap} characters")
    
    documents = []
    mongo_documents = []
    processed_pages = 0
    
    org_search_client = get_search_client(org_id)
    safe_org_id = sanitize_azure_name(org_id)
    
    # Create a knowledge source for this batch
    source_name = f"Web Scraping - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    source_description = f"Website content scraped and processed"
    
    try:
        for page_data in scraped_content:
            url = page_data.get('url', '')
            title = page_data.get('title', 'No Title')
            content = page_data.get('content', '')
            metadata = page_data.get('metadata', {})
            
            if not content.strip():
                print(f"Warning: No content extracted from {url}")
                continue
                
            print(f"Processing page: {title} ({url})")
            
            # Chunk the content
            chunks = chunk_text(content, chunk_size, overlap)
            print(f"Page '{title}' split into {len(chunks)} chunks")
            
            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    # Azure Search document
                    document = {
                        "id": f"{safe_org_id}_web_{url.replace('://', '_').replace('/', '_').replace('.', '_')}_{i}",
                        "content": chunk,
                        "filepath": url,  # Using URL as filepath for web content
                        "organization_id": org_id,
                        "blob_name": f"web_content_{url.replace('://', '_').replace('/', '_')}",  # Virtual blob name
                        "embedding": generate_embeddings(chunk)
                    }
                    documents.append(document)
                    
                    # MongoDB document metadata
                    mongo_doc = {
                        "title": f"{title} - Chunk {i+1}",
                        "content": chunk,
                        "url": url,
                        "metadata": {
                            "url": url,
                            "title": title,
                            "chunk_index": i,
                            "total_chunks": len(chunks),
                            "processed_at": datetime.utcnow().isoformat(),
                            "source": "web_scraping",
                            "chunk_size": len(chunk),
                            "organization_id": org_id,
                            "scraped_metadata": metadata
                        }
                    }
                    mongo_documents.append(mongo_doc)
            
            processed_pages += 1
        
        print(f"Processed {processed_pages} pages for organization '{org_id}'")
        
        # Upload to Azure Search
        if documents:
            try:
                org_search_client.merge_or_upload_documents(documents=documents)
                print(f"Uploaded {len(documents)} web scraping documents to organization '{org_id}' search index.")
            except AttributeError:
                try:
                    org_search_client.upload_documents(documents=documents, merge_mode="mergeOrUpload")
                    print(f"Uploaded {len(documents)} web scraping documents to organization '{org_id}' search index.")
                except TypeError:
                    print("Warning: Using basic upload - may create duplicates on re-runs")
                    org_search_client.upload_documents(documents=documents)
                    print(f"Uploaded {len(documents)} web scraping documents to organization '{org_id}' search index.")
        else:
            print("No new web scraping documents to upload to Azure Search.")
        
        # Store metadata in MongoDB
        if mongo_documents:
            try:
                configuration = {
                    "chunk_size": chunk_size,
                    "overlap": overlap,
                    "processed_pages": processed_pages,
                    "total_chunks": len(mongo_documents),
                    "processing_type": "web_scraping"
                }
                
                source_id, document_ids = KnowledgeService.process_file_batch(
                    organization_id=org_id,
                    source_name=source_name,
                    description=source_description,
                    file_data=mongo_documents,
                    configuration=configuration
                )
                
                print(f"Stored metadata for {len(document_ids)} web scraping documents in MongoDB")
                print(f"Knowledge source ID: {source_id}")
                
            except Exception as e:
                print(f"Error storing web scraping metadata in MongoDB: {e}")
                print("Azure Search documents uploaded successfully, but MongoDB storage failed")
        else:
            print("No web scraping documents to store in MongoDB.")
            
    except Exception as e:
        print(f"Error during web scraping content processing: {e}")
        raise

async def scrape_and_process_website(org_id: str, url: str, 
                                   chunk_size: int = DEFAULT_CHUNK_SIZE, 
                                   overlap: int = DEFAULT_CHUNK_OVERLAP):
    """
    Scrape a website and process the content for Azure AI Search RAG
    
    Args:
        org_id (str): Organization identifier
        url (str): Website URL to scrape
        chunk_size (int): Maximum size of each chunk in characters
        overlap (int): Number of characters to overlap between chunks
    """
    try:
        print(f"Starting web scraping for organization '{org_id}' from URL: {url}")
        
        # Scrape the website
        scraped_content = await scrape_website(url)
        
        if not scraped_content:
            print(f"No content was scraped from {url}")
            raise ValueError(f"No content was scraped from {url} - check if the page is accessible and scrapeable")
        
        # Process and upload the scraped content
        await process_and_upload_scraped_content(org_id, scraped_content, chunk_size, overlap)
        
        print(f"Web scraping completed successfully for organization '{org_id}'")
        
    except Exception as e:
        print(f"Error during web scraping for organization '{org_id}': {e}")
        raise

def scrape_and_process_website_sync(org_id: str, url: str, 
                                  chunk_size: int = DEFAULT_CHUNK_SIZE, 
                                  overlap: int = DEFAULT_CHUNK_OVERLAP):
    """
    Synchronous wrapper for scrape_and_process_website
    
    Args:
        org_id (str): Organization identifier
        url (str): Website URL to scrape
        chunk_size (int): Maximum size of each chunk in characters
        overlap (int): Number of characters to overlap between chunks
    """
    try:
        # Run the async function
        asyncio.run(scrape_and_process_website(org_id, url, chunk_size, overlap))
    except Exception as e:
        print(f"Error in synchronous web scraping wrapper: {e}")
        raise
