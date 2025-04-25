"""
Main pipeline for transferring documents from Elasticsearch to Pinecone.
"""

import logging
import concurrent.futures
from typing import Dict, List, Any, Optional, Callable
from tqdm import tqdm

from .elasticsearch_client import ElasticsearchClient
from .pinecone_client import PineconeClient
from .embeddings import create_embedding_generator
from .utils import (
    load_config, 
    validate_config, 
    setup_logging, 
    create_text_for_embedding,
    extract_fields,
    chunk_list
)
from .exceptions import ESPipelineError, BatchProcessingError

logger = logging.getLogger(__name__)

class ElasticsearchToPineconePipeline:
    """Pipeline for transferring documents from Elasticsearch to Pinecone."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, env_path: Optional[str] = None):
        """
        Initialize the pipeline.
        
        Args:
            config: Optional configuration dictionary (overrides .env)
            env_path: Optional path to .env file
        """
        # Setup logging
        setup_logging()
        
        # Load configuration
        self.config = config or load_config(env_path)
        validate_config(self.config)
        
        # Initialize clients
        self.es_client = ElasticsearchClient(self.config)
        self.pinecone_client = PineconeClient(self.config)
        self.embedding_generator = create_embedding_generator(self.config)
        
        # Pipeline settings
        self.batch_size = self.config.get('batch_size', 100)
        self.max_threads = self.config.get('max_threads', 5)
        self.fields_to_embed = self.config.get('fields_to_embed', [])
        self.metadata_fields = self.config.get('metadata_fields', [])
        
        # Optional callbacks
        self.progress_callback = None
        self.field_mapping = None
    
    def set_progress_callback(self, callback: Callable[[int, int], None]) -> None:
        """
        Set a callback function for progress updates.
        
        Args:
            callback: Function taking (current_batch, total_batches)
        """
        self.progress_callback = callback
    
    def set_field_mapping(self, mapping: Dict[str, str]) -> None:
        """
        Set field mapping for document processing.
        
        Args:
            mapping: Dictionary mapping source fields to target fields
        """
        self.field_mapping = mapping
    
    def _process_batch(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process a batch of documents.
        
        Args:
            documents: List of Elasticsearch documents
            
        Returns:
            List of vectors ready for Pinecone upsert
        """
        vectors = []
        
        try:
            # Apply field mapping if set
            if self.field_mapping:
                mapped_documents = []
                for doc in documents:
                    mapped_doc = {}
                    for source_field, target_field in self.field_mapping.items():
                        if source_field in doc:
                            mapped_doc[target_field] = doc[source_field]
                        else:
                            mapped_doc[target_field] = None
                    mapped_doc['_id'] = doc['_id']  # Preserve document ID
                    mapped_documents.append(mapped_doc)
                documents = mapped_documents
            
            # Extract text for embedding
            texts = []
            for doc in documents:
                text = create_text_for_embedding(doc, self.fields_to_embed)
                texts.append(text)
            
            # Generate embeddings
            embeddings = self.embedding_generator.generate_embeddings(texts)
            
            # Create vectors with metadata
            for i, doc in enumerate(documents):
                metadata = extract_fields(doc, self.metadata_fields)
                
                # Add original text to metadata if needed
                if 'original_text' not in metadata:
                    metadata['original_text'] = texts[i][:1000]  # Limit text length
                
                vector = {
                    'id': doc['_id'],
                    'values': embeddings[i],
                    'metadata': metadata
                }
                vectors.append(vector)
            
            return vectors
            
        except Exception as e:
            logger.error(f"Error processing batch: {str(e)}")
            raise BatchProcessingError(f"Failed to process batch: {str(e)}")
    
    def _process_and_upsert_batch(self, documents: List[Dict[str, Any]]) -> int:
        """
        Process a batch of documents and upsert to Pinecone.
        
        Args:
            documents: List of Elasticsearch documents
            
        Returns:
            Number of vectors upserted
        """
        try:
            vectors = self._process_batch(documents)
            result = self.pinecone_client.upsert_vectors(vectors)
            return result.get('upserted_count', 0)
        except Exception as e:
            logger.error(f"Error processing and upserting batch: {str(e)}")
            return 0
    
    def run(self, 
            query: Optional[Dict[str, Any]] = None,
            dry_run: bool = False) -> Dict[str, Any]:
        """
        Run the pipeline to transfer documents from Elasticsearch to Pinecone.
        
        Args:
            query: Optional Elasticsearch query to filter documents
            dry_run: If True, process documents but don't upsert to Pinecone
            
        Returns:
            Dictionary with transfer statistics
        """
        try:
            logger.info("Starting Elasticsearch to Pinecone transfer pipeline")
            
            # Get total document count
            total_docs = self.es_client.get_document_count()
            logger.info(f"Total documents to process: {total_docs}")
            
            if total_docs == 0:
                logger.warning("No documents found in Elasticsearch index")
                return {'processed': 0, 'upserted': 0, 'failed': 0}
            
            # Scan documents from Elasticsearch
            documents = self.es_client.scan_documents(
                batch_size=self.batch_size,
                query=query,
                fields=None  # Get all fields
            )
            
            # Split into batches
            batches = chunk_list(documents, self.batch_size)
            total_batches = len(batches)
            
            # Process batches with thread pool
            processed = 0
            upserted = 0
            failed = 0
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_threads) as executor:
                # Create progress bar
                with tqdm(total=total_batches, desc="Processing batches") as pbar:
                    # Submit all batches
                    future_to_batch = {
                        executor.submit(self._process_and_upsert_batch, batch): i 
                        for i, batch in enumerate(batches)
                    }
                    
                    # Process completed batches
                    for future in concurrent.futures.as_completed(future_to_batch):
                        batch_idx = future_to_batch[future]
                        try:
                            if dry_run:
                                # In dry run, just process without upserting
                                self._process_batch(batches[batch_idx])
                                upserted_count = len(batches[batch_idx])
                            else:
                                upserted_count = future.result()
                            
                            upserted += upserted_count
                            processed += len(batches[batch_idx])
                            
                            # Update progress
                            pbar.update(1)
                            
                            # Call progress callback if set
                            if self.progress_callback:
                                self.progress_callback(batch_idx + 1, total_batches)
                            
                        except Exception as e:
                            logger.error(f"Batch {batch_idx} failed: {str(e)}")
                            failed += len(batches[batch_idx])
                            pbar.update(1)
            
            # Summary
            stats = {
                'processed': processed,
                'upserted': upserted,
                'failed': failed,
                'total_documents': total_docs,
                'success_rate': (upserted / processed * 100) if processed > 0 else 0
            }
            
            logger.info(f"Pipeline completed. {processed} documents processed, "
                       f"{upserted} upserted, {failed} failed.")
            
            return stats
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            raise ESPipelineError(f"Pipeline execution failed: {str(e)}")

def main():
    """Command-line interface for the pipeline."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Transfer documents from Elasticsearch to Pinecone")
    parser.add_argument("--env", help="Path to .env file", default=None)
    parser.add_argument("--dry-run", action="store_true", help="Process documents without upserting")
    parser.add_argument("--query", help="Elasticsearch query (JSON string)", default=None)
    
    args = parser.parse_args()
    
    # Parse query if provided
    query = None
    if args.query:
        import json
        try:
            query = json.loads(args.query)
        except json.JSONDecodeError:
            logger.error("Invalid JSON query string")
            return
    
    try:
        pipeline = ElasticsearchToPineconePipeline(env_path=args.env)
        stats = pipeline.run(query=query, dry_run=args.dry_run)
        
        print("\nTransfer Statistics:")
        print(f"Total documents: {stats['total_documents']}")
        print(f"Processed: {stats['processed']}")
        print(f"Upserted: {stats['upserted']}")
        print(f"Failed: {stats['failed']}")
        print(f"Success rate: {stats['success_rate']:.2f}%")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()