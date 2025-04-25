#!/usr/bin/env python
"""
Example of semantic search using the vectors in Pinecone
after transferring documents from Elasticsearch.
"""

import os
import logging
import argparse
from dotenv import load_dotenv
from es_to_pinecone_transfer.pipeline import ElasticsearchToPineconePipeline
from es_to_pinecone_transfer.embeddings import create_embedding_generator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def search_pinecone(query, top_k=5, namespace=None):
    """
    Search Pinecone with a text query.
    
    Args:
        query: Text query to search for
        top_k: Number of results to return
        namespace: Pinecone namespace to search in
    
    Returns:
        List of search results
    """
    # Load environment variables
    load_dotenv()
    
    # Initialize the pipeline (just to get the clients and config)
    pipeline = ElasticsearchToPineconePipeline()
    
    # Get the embedding generator
    embedding_generator = create_embedding_generator(pipeline.config)
    
    # Generate embedding for the query
    logger.info(f"Generating embedding for query: '{query}'")
    query_embedding = embedding_generator.generate_embeddings([query])[0]
    
    # Query Pinecone
    logger.info(f"Searching Pinecone for query: '{query}'")
    namespace = namespace or pipeline.config.get('default_namespace', 'default')
    results = pipeline.pinecone_client.query_vectors(
        vector=query_embedding,
        top_k=top_k,
        namespace=namespace,
        include_metadata=True
    )
    
    return results

def display_results(results):
    """Display search results in a readable format."""
    if not results:
        print("No results found.")
        return
    
    print(f"\nFound {len(results)} results:\n")
    for i, match in enumerate(results):
        print(f"Result #{i+1} (Score: {match['score']:.4f}, ID: {match['id']})")
        
        # Print metadata
        if 'metadata' in match:
            metadata = match['metadata']
            
            # Print title if available
            if 'title' in metadata or 'document_title' in metadata:
                title = metadata.get('title') or metadata.get('document_title')
                print(f"Title: {title}")
            
            # Print author if available
            if 'author' in metadata or 'document_author' in metadata:
                author = metadata.get('author') or metadata.get('document_author')
                print(f"Author: {author}")
            
            # Print a snippet of the content if available
            content_field = None
            for field in ['content', 'document_content', 'text', 'original_text', 'body']:
                if field in metadata and metadata[field]:
                    content_field = field
                    break
            
            if content_field:
                content = metadata[content_field]
                max_length = 200
                snippet = content[:max_length] + ("..." if len(content) > max_length else "")
                print(f"Content: {snippet}")
            
            # Print other metadata fields
            for key, value in metadata.items():
                if key not in ['title', 'document_title', 'author', 'document_author', content_field]:
                    if isinstance(value, str) and len(value) > 50:
                        value = value[:50] + "..."
                    print(f"{key}: {value}")
        
        print("-" * 80)

def main():
    parser = argparse.ArgumentParser(description="Semantic search using Pinecone")
    parser.add_argument("query", help="The search query")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results to return")
    parser.add_argument("--namespace", help="Pinecone namespace to search in")
    args = parser.parse_args()
    
    try:
        results = search_pinecone(args.query, args.top_k, args.namespace)
        display_results(results)
    except Exception as e:
        logger.error(f"Error during search: {str(e)}")
        raise

if __name__ == "__main__":
    main()
