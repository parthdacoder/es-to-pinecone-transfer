"""
Elasticsearch client for reading documents.
"""

import logging
from typing import Dict, List, Any, Optional
from elasticsearch import Elasticsearch
import elastic_transport

# Handle different exception imports for different elasticsearch versions
try:
    from elasticsearch.exceptions import ConnectionError as ESConnectionError, AuthenticationException
except (ImportError, ModuleNotFoundError):
    # For newer versions of elasticsearch
    ESConnectionError = elastic_transport.ConnectionError
    AuthenticationException = Exception  # Fallback if not available

from .exceptions import ElasticsearchConnectionError
from .utils import extract_fields

logger = logging.getLogger(__name__)

class ElasticsearchClient:
    """Client for interacting with Elasticsearch."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Elasticsearch client.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.client = self._create_client()
        self.index = config['es_index']
        
    def _create_client(self) -> Elasticsearch:
        """Create Elasticsearch client instance."""
        try:
            client_args = {
                'hosts': [self.config['es_host']],
                'verify_certs': True,
                'ca_certs': None
            }
            
            # Use API key if available
            if self.config.get('es_api_key'):
                client_args['api_key'] = self.config['es_api_key']
            # Otherwise use username/password if available
            elif self.config.get('es_username') and self.config.get('es_password'):
                client_args['basic_auth'] = (self.config['es_username'], self.config['es_password'])
            
            client = Elasticsearch(**client_args)
            
            # Test connection
            if not client.ping():
                raise ElasticsearchConnectionError("Failed to connect to Elasticsearch")
            
            logger.info(f"Successfully connected to Elasticsearch at {self.config['es_host']}")
            return client
            
        except ESConnectionError as e:
            raise ElasticsearchConnectionError(f"Connection failed: {str(e)}")
        except AuthenticationException as e:
            raise ElasticsearchConnectionError(f"Authentication failed: {str(e)}")
        except Exception as e:
            raise ElasticsearchConnectionError(f"Unexpected error: {str(e)}")
    
    def get_document_count(self) -> int:
        """Get total number of documents in the index."""
        try:
            count = self.client.count(index=self.index)
            return count['count']
        except Exception as e:
            logger.error(f"Error getting document count: {str(e)}")
            return 0
    
    def scan_documents(self, 
                      batch_size: int = 100, 
                      query: Optional[Dict[str, Any]] = None,
                      fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Scan through documents in the index with pagination.
        
        Args:
            batch_size: Number of documents per batch
            query: Optional Elasticsearch query
            fields: Optional list of fields to retrieve
            
        Returns:
            List of documents
        """
        try:
            search_args = {
                'index': self.index,
                'scroll': '5m',
                'size': batch_size,
                'body': query or {'query': {'match_all': {}}}
            }
            
            if fields:
                search_args['_source'] = fields
            
            # Initialize scroll
            response = self.client.search(**search_args)
            scroll_id = response['_scroll_id']
            documents = []
            
            while True:
                # Extract documents from response
                hits = response['hits']['hits']
                if not hits:
                    break
                
                for hit in hits:
                    doc = hit['_source']
                    doc['_id'] = hit['_id']  # Include document ID
                    documents.append(doc)
                
                # Get next batch
                response = self.client.scroll(scroll_id=scroll_id, scroll='5m')
            
            # Clear scroll
            self.client.clear_scroll(scroll_id=scroll_id)
            
            return documents
            
        except Exception as e:
            logger.error(f"Error scanning documents: {str(e)}")
            raise ElasticsearchConnectionError(f"Failed to scan documents: {str(e)}")
    
    def get_documents_by_ids(self, doc_ids: List[str], fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Get documents by IDs.
        
        Args:
            doc_ids: List of document IDs
            fields: Optional list of fields to retrieve
            
        Returns:
            List of documents
        """
        try:
            body = {
                'ids': doc_ids
            }
            
            if fields:
                body['_source'] = fields
            
            response = self.client.mget(
                index=self.index,
                body=body
            )
            
            documents = []
            for doc in response['docs']:
                if doc.get('found'):
                    doc_data = doc['_source']
                    doc_data['_id'] = doc['_id']
                    documents.append(doc_data)
            
            return documents
            
        except Exception as e:
            logger.error(f"Error getting documents by IDs: {str(e)}")
            return []
    
    def search_documents(self, 
                        query: Dict[str, Any], 
                        size: int = 100,
                        fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Search for documents using a query.
        
        Args:
            query: Elasticsearch query
            size: Maximum number of documents to return
            fields: Optional list of fields to retrieve
            
        Returns:
            List of documents
        """
        try:
            search_args = {
                'index': self.index,
                'body': {'query': query},
                'size': size
            }
            
            if fields:
                search_args['_source'] = fields
            
            response = self.client.search(**search_args)
            
            documents = []
            for hit in response['hits']['hits']:
                doc = hit['_source']
                doc['_id'] = hit['_id']
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []