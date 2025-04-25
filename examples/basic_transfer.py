#!/usr/bin/env python
"""
Basic example of transferring documents from Elasticsearch to Pinecone.
"""

import os
import logging
from dotenv import load_dotenv
from es_to_pinecone_transfer.pipeline import ElasticsearchToPineconePipeline

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Log the configuration (excluding sensitive values)
    logger.info(f"Elasticsearch Host: {os.getenv('ES_HOST')}")
    logger.info(f"Elasticsearch Index: {os.getenv('ES_INDEX')}")
    logger.info(f"Pinecone Index: {os.getenv('PINECONE_INDEX_NAME')}")
    logger.info(f"Embedding Type: {os.getenv('EMBEDDING_TYPE')}")
    
    try:
        # Initialize the pipeline
        logger.info("Initializing the pipeline...")
        pipeline = ElasticsearchToPineconePipeline()
        
        # Get document count from Elasticsearch
        es_count = pipeline.es_client.get_document_count()
        logger.info(f"Found {es_count} documents in Elasticsearch index")
        
        # Run the pipeline
        logger.info("Starting transfer process...")
        stats = pipeline.run()
        
        # Log results
        logger.info("Transfer completed!")
        logger.info(f"Documents processed: {stats['processed']}")
        logger.info(f"Documents upserted to Pinecone: {stats['upserted']}")
        logger.info(f"Documents that failed: {stats['failed']}")
        logger.info(f"Success rate: {stats['success_rate']:.2f}%")
        
        # Get Pinecone index stats
        pinecone_stats = pipeline.pinecone_client.get_index_stats()
        logger.info(f"Pinecone index now contains {pinecone_stats.get('total_vector_count', 0)} vectors")
        
    except Exception as e:
        logger.error(f"Error during transfer: {str(e)}")
        raise

if __name__ == "__main__":
    main()
