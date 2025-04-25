"""
Pinecone client for upserting vectors.
"""

import logging
from typing import Dict, List, Any, Optional
import pinecone

from .exceptions import PineconeConnectionError
from .utils import extract_fields

logger = logging.getLogger(__name__)

class PineconeClient:
    """Client for interacting with Pinecone."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Pinecone client.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.index = self._initialize_pinecone()
        
    def _initialize_pinecone(self):
        """Initialize Pinecone connection and index."""
        try:
            # Initialize using the older pinecone-client style
            api_key = self.config['pinecone_api_key']
            pinecone.init(api_key=api_key)
            
            # Check if index exists
            index_name = self.config['pinecone_index_name']
            
            # List existing indexes
            if index_name not in pinecone.list_indexes():
                logger.warning(f"Index '{index_name}' does not exist. Creating it now...")
                
                # Create index (adjust dimension based on embedding model)
                dimension = 1536  # Default for OpenAI's text-embedding-ada-002
                if self.config['embedding_type'] == 'huggingface':
                    # Adjust dimension based on model
                    if 'all-MiniLM-L6-v2' in self.config.get('huggingface_model', ''):
                        dimension = 384
                
                # Create the index using the older API style
                pinecone.create_index(
                    name=index_name,
                    dimension=dimension,
                    metric="cosine"
                )
                logger.info(f"Created Pinecone index '{index_name}' with dimension {dimension}")
            
            # Connect to index
            index = pinecone.Index(index_name)
            logger.info(f"Successfully connected to Pinecone index '{index_name}'")
            
            return index
            
        except Exception as e:
            raise PineconeConnectionError(f"Failed to initialize Pinecone: {str(e)}")
    
    def upsert_vectors(self, 
                      vectors: List[Dict[str, Any]], 
                      namespace: Optional[str] = None) -> Dict[str, int]:
        """
        Upsert vectors to Pinecone.
        
        Args:
            vectors: List of vector dictionaries with id, values, and metadata
            namespace: Optional namespace to use
            
        Returns:
            Dictionary with upsert statistics
        """
        try:
            if not vectors:
                return {'upserted_count': 0}
            
            # Use default namespace if not provided
            namespace = namespace or self.config.get('default_namespace', 'default')
            
            # Prepare vectors for upsert
            formatted_vectors = []
            for vector in vectors:
                if not all(key in vector for key in ['id', 'values']):
                    logger.warning(f"Skipping vector with missing id or values: {vector}")
                    continue
                
                formatted_vector = {
                    'id': str(vector['id']),
                    'values': vector['values']
                }
                
                if 'metadata' in vector and vector['metadata']:
                    formatted_vector['metadata'] = vector['metadata']
                
                formatted_vectors.append(formatted_vector)
            
            if not formatted_vectors:
                return {'upserted_count': 0}
            
            # Upsert to Pinecone
            upsert_response = self.index.upsert(
                vectors=formatted_vectors, 
                namespace=namespace
            )
            
            # Return the result - in older versions this is a dict, not an object
            if isinstance(upsert_response, dict) and 'upserted_count' in upsert_response:
                return {'upserted_count': upsert_response['upserted_count']}
            else:
                # Fallback
                return {'upserted_count': len(formatted_vectors)}
            
        except Exception as e:
            logger.error(f"Error upserting vectors: {str(e)}")
            raise PineconeConnectionError(f"Failed to upsert vectors: {str(e)}")
    
    def delete_vectors(self, 
                      ids: List[str], 
                      namespace: Optional[str] = None) -> bool:
        """
        Delete vectors from Pinecone.
        
        Args:
            ids: List of vector IDs to delete
            namespace: Optional namespace
            
        Returns:
            True if successful
        """
        try:
            namespace = namespace or self.config.get('default_namespace', 'default')
            self.index.delete(ids=ids, namespace=namespace)
            return True
        except Exception as e:
            logger.error(f"Error deleting vectors: {str(e)}")
            return False
    
    def query_vectors(self, 
                     vector: List[float], 
                     top_k: int = 10, 
                     namespace: Optional[str] = None, 
                     include_metadata: bool = True) -> List[Dict[str, Any]]:
        """
        Query vectors from Pinecone.
        
        Args:
            vector: Query vector
            top_k: Number of results to return
            namespace: Optional namespace
            include_metadata: Whether to include metadata in results
            
        Returns:
            List of matches
        """
        try:
            namespace = namespace or self.config.get('default_namespace', 'default')
            
            # Query using the older Pinecone client style
            response = self.index.query(
                vector=vector,
                top_k=top_k,
                namespace=namespace,
                include_metadata=include_metadata
            )
            
            matches = []
            
            # Process matches from the response
            if 'matches' in response:
                for match in response['matches']:
                    result = {
                        'id': match.get('id'),
                        'score': match.get('score')
                    }
                    if include_metadata and 'metadata' in match:
                        result['metadata'] = match['metadata']
                    matches.append(result)
            
            return matches
            
        except Exception as e:
            logger.error(f"Error querying vectors: {str(e)}")
            return []
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the Pinecone index.
        
        Returns:
            Dictionary with index statistics
        """
        try:
            stats = self.index.describe_index_stats()
            return stats
        except Exception as e:
            logger.error(f"Error getting index stats: {str(e)}")
            return {}
    
    def clear_namespace(self, namespace: Optional[str] = None) -> bool:
        """
        Clear all vectors in a namespace.
        
        Args:
            namespace: Namespace to clear (defaults to configured namespace)
            
        Returns:
            True if successful
        """
        try:
            namespace = namespace or self.config.get('default_namespace', 'default')
            self.index.delete(delete_all=True, namespace=namespace)
            logger.info(f"Cleared namespace '{namespace}'")
            return True
        except Exception as e:
            logger.error(f"Error clearing namespace: {str(e)}")
            return False