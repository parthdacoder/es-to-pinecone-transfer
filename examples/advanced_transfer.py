#!/usr/bin/env python
"""
Advanced example of transferring documents from Elasticsearch to Pinecone
with progress tracking, field mapping, and query filtering.
"""

import os
import time
import logging
from dotenv import load_dotenv
from es_to_pinecone_transfer.pipeline import ElasticsearchToPineconePipeline
from es_to_pinecone_transfer.exceptions import ESPipelineError

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("transfer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def progress_callback(current_batch, total_batches):
    """Progress callback function for the pipeline."""
    percent = (current_batch / total_batches) * 100 if total_batches > 0 else 0
    logger.info(f"Progress: {current_batch}/{total_batches} ({percent:.2f}%)")

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Custom configuration (overrides .env file values)
    config = {
        # Elasticsearch Configuration
        'es_host': os.getenv('ES_HOST', 'http://localhost:9200'),
        'es_username': os.getenv('ES_USERNAME'),
        'es_password': os.getenv('ES_PASSWORD'),
        'es_index': os.getenv('ES_INDEX'),
        
        # Embedding Configuration
        'embedding_type': os.getenv('EMBEDDING_TYPE', 'openai'),
        'openai_api_key': os.getenv('OPENAI_API_KEY'),
        'openai_model': os.getenv('OPENAI_MODEL', 'text-embedding-ada-002'),
        
        # Pinecone Configuration
        'pinecone_api_key': os.getenv('PINECONE_API_KEY'),
        'pinecone_environment': os.getenv('PINECONE_ENVIRONMENT'),
        'pinecone_index_name': os.getenv('PINECONE_INDEX_NAME'),
        
        # Pipeline Configuration
        'batch_size': int(os.getenv('BATCH_SIZE', '50')),
        'max_threads': int(os.getenv('MAX_THREADS', '4')),
        'fields_to_embed': os.getenv('FIELDS_TO_EMBED', '').split(','),
        'metadata_fields': os.getenv('METADATA_FIELDS', '').split(','),
        'default_namespace': os.getenv('DEFAULT_NAMESPACE', 'default')
    }
    
    # Clean up empty fields
    config['fields_to_embed'] = [f.strip() for f in config['fields_to_embed'] if f.strip()]
    config['metadata_fields'] = [f.strip() for f in config['metadata_fields'] if f.strip()]
    
    # Field mapping (optional)
    field_mapping = {
        'title': 'document_title',
        'content': 'document_content',
        'author': 'document_author'
    }
    
    # Query to filter documents (optional)
    query = {
        "bool": {
            "must": [
                {"term": {"status": "published"}},
                {"range": {"publish_date": {"gte": "2023-01-01"}}}
            ]
        }
    }
    
    try:
        # Initialize the pipeline with custom config
        logger.info("Initializing the pipeline with custom configuration...")
        pipeline = ElasticsearchToPineconePipeline(config=config)
        
        # Set field mapping if needed
        if field_mapping:
            logger.info(f"Setting field mapping: {field_mapping}")
            pipeline.set_field_mapping(field_mapping)
        
        # Set progress callback
        pipeline.set_progress_callback(progress_callback)
        
        # Perform a dry run first
        logger.info("Starting dry run...")
        start_time = time.time()
        dry_run_stats = pipeline.run(query=query, dry_run=True)
        dry_run_time = time.time() - start_time
        
        logger.info(f"Dry run completed in {dry_run_time:.2f} seconds")
        logger.info(f"Would process {dry_run_stats['processed']} documents")
        
        # Ask for confirmation
        if os.getenv('AUTO_CONFIRM', 'false').lower() != 'true':
            confirmation = input("Proceed with actual transfer? (y/n): ")
            if confirmation.lower() != 'y':
                logger.info("Transfer aborted by user")
                return
        
        # Run the actual transfer
        logger.info("Starting actual transfer...")
        start_time = time.time()
        stats = pipeline.run(query=query)
        total_time = time.time() - start_time
        
        # Log results
        logger.info(f"Transfer completed in {total_time:.2f} seconds!")
        logger.info(f"Documents processed: {stats['processed']}")
        logger.info(f"Documents upserted to Pinecone: {stats['upserted']}")
        logger.info(f"Documents that failed: {stats['failed']}")
        logger.info(f"Success rate: {stats['success_rate']:.2f}%")
        logger.info(f"Average processing time per document: {total_time/stats['processed']:.4f} seconds")
        
        # Get Pinecone index stats
        pinecone_stats = pipeline.pinecone_client.get_index_stats()
        logger.info(f"Pinecone index now contains {pinecone_stats.get('total_vector_count', 0)} vectors")
        
        # Print namespace statistics if available
        if 'namespaces' in pinecone_stats:
            logger.info("Namespace statistics:")
            for namespace, ns_stats in pinecone_stats['namespaces'].items():
                logger.info(f"  {namespace}: {ns_stats.get('vector_count', 0)} vectors")
        
    except ESPipelineError as e:
        logger.error(f"Pipeline error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
