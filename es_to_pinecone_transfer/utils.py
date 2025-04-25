"""
Utility functions for the ES to Pinecone transfer pipeline.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def load_config(env_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from environment variables.
    
    Args:
        env_path: Optional path to .env file
        
    Returns:
        Dictionary containing configuration values
    """
    if env_path:
        load_dotenv(env_path)
    else:
        load_dotenv()
    
    config = {
        # Elasticsearch Configuration
        'es_host': os.getenv('ES_HOST', 'http://localhost:9200'),
        'es_username': os.getenv('ES_USERNAME'),
        'es_password': os.getenv('ES_PASSWORD'),
        'es_api_key': os.getenv('ES_API_KEY'),
        'es_index': os.getenv('ES_INDEX'),
        
        # Embedding Configuration
        'embedding_type': os.getenv('EMBEDDING_TYPE', 'openai'),
        'openai_api_key': os.getenv('OPENAI_API_KEY'),
        'openai_model': os.getenv('OPENAI_MODEL', 'text-embedding-ada-002'),
        'huggingface_model': os.getenv('HUGGINGFACE_MODEL', 'sentence-transformers/all-MiniLM-L6-v2'),
        
        # Pinecone Configuration
        'pinecone_api_key': os.getenv('PINECONE_API_KEY'),
        'pinecone_environment': os.getenv('PINECONE_ENVIRONMENT'),
        'pinecone_index_name': os.getenv('PINECONE_INDEX_NAME'),
        
        # Pipeline Configuration
        'batch_size': int(os.getenv('BATCH_SIZE', '100')),
        'max_threads': int(os.getenv('MAX_THREADS', '5')),
        'fields_to_embed': os.getenv('FIELDS_TO_EMBED', '').split(','),
        'metadata_fields': os.getenv('METADATA_FIELDS', '').split(','),
        'default_namespace': os.getenv('DEFAULT_NAMESPACE', 'default')
    }
    
    # Clean up empty fields
    config['fields_to_embed'] = [f.strip() for f in config['fields_to_embed'] if f.strip()]
    config['metadata_fields'] = [f.strip() for f in config['metadata_fields'] if f.strip()]
    
    return config

def extract_fields(document: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
    """
    Extract specified fields from a document.
    
    Args:
        document: Source document
        fields: List of field names to extract
        
    Returns:
        Dictionary containing extracted fields
    """
    result = {}
    for field in fields:
        if '.' in field:  # Handle nested fields
            parts = field.split('.')
            value = document
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    value = None
                    break
            if value is not None:
                result[field] = value
        elif field in document:
            result[field] = document[field]
    return result

def create_text_for_embedding(document: Dict[str, Any], fields: List[str]) -> str:
    """
    Create a text string from specified fields for embedding.
    
    Args:
        document: Source document
        fields: List of field names to combine
        
    Returns:
        Combined text string
    """
    extracted = extract_fields(document, fields)
    texts = []
    
    for field, value in extracted.items():
        if isinstance(value, (list, dict)):
            texts.append(f"{field}: {str(value)}")
        else:
            texts.append(str(value))
    
    return " ".join(texts)

def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Setup logging configuration.
    
    Args:
        log_level: Logging level
        log_file: Optional file path for logging
    """
    handlers = [logging.StreamHandler()]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate the configuration values.
    
    Args:
        config: Configuration dictionary
        
    Raises:
        ConfigurationError: If configuration is invalid
    """
    from .exceptions import ConfigurationError
    
    required_fields = {
        'es_index': 'Elasticsearch index name',
        'pinecone_api_key': 'Pinecone API key',
        'pinecone_environment': 'Pinecone environment',
        'pinecone_index_name': 'Pinecone index name',
        'fields_to_embed': 'Fields to embed from ES documents'
    }
    
    for field, description in required_fields.items():
        if not config.get(field):
            raise ConfigurationError(f"Missing required configuration: {description}")
    
    if config['embedding_type'] == 'openai' and not config.get('openai_api_key'):
        raise ConfigurationError("OpenAI API key is required when using OpenAI embeddings")
    
    if not config.get('es_api_key') and not (config.get('es_username') and config.get('es_password')):
        logger.warning("No Elasticsearch authentication provided. Attempting to connect without authentication.")

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of specified size.
    
    Args:
        lst: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]