"""
Embedding generators for the ES to Pinecone transfer pipeline.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import numpy as np

from .exceptions import EmbeddingError, ConfigurationError

logger = logging.getLogger(__name__)

class BaseEmbeddingGenerator(ABC):
    """Base class for embedding generators."""
    
    @abstractmethod
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """Get the dimension of the embeddings."""
        pass

class OpenAIEmbeddingGenerator(BaseEmbeddingGenerator):
    """OpenAI embedding generator."""
    
    def __init__(self, api_key: str, model: str = "text-embedding-ada-002"):
        """
        Initialize OpenAI embedding generator.
        
        Args:
            api_key: OpenAI API key
            model: Model to use for embeddings
        """
        self.api_key = api_key
        self.model = model
        
        # Model dimensions mapping
        self.model_dimensions = {
            'text-embedding-ada-002': 1536,
            'text-embedding-3-small': 1536,
            'text-embedding-3-large': 3072
        }
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API."""
        try:
            if not texts:
                return []
            
            # Remove empty strings
            texts = [text for text in texts if text.strip()]
            if not texts:
                return []
            
            # Import OpenAI inside the method to handle import errors gracefully
            import openai
            
            try:
                # Try the newer OpenAI client approach
                from openai import OpenAI
                client = OpenAI(api_key=self.api_key)
                response = client.embeddings.create(model=self.model, input=texts)
                embeddings = [data.embedding for data in response.data]
            except (ImportError, AttributeError):
                # Fall back to the older approach
                openai.api_key = self.api_key
                response = openai.Embedding.create(model=self.model, input=texts)
                embeddings = [data['embedding'] for data in response['data']]
                
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating OpenAI embeddings: {str(e)}")
            raise EmbeddingError(f"Failed to generate embeddings: {str(e)}")
    
    def get_dimension(self) -> int:
        """Get the dimension of the embeddings."""
        return self.model_dimensions.get(self.model, 1536)

class HuggingFaceEmbeddingGenerator(BaseEmbeddingGenerator):
    """HuggingFace embedding generator."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize HuggingFace embedding generator.
        
        Args:
            model_name: HuggingFace model to use
        """
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            self.model_name = model_name
        except ImportError:
            raise EmbeddingError(
                "sentence-transformers package not installed. Install with: pip install sentence-transformers"
            )
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using HuggingFace model."""
        try:
            if not texts:
                return []
            
            # Remove empty strings
            texts = [text for text in texts if text.strip()]
            if not texts:
                return []
            
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
            
        except Exception as e:
            logger.error(f"Error generating HuggingFace embeddings: {str(e)}")
            raise EmbeddingError(f"Failed to generate embeddings: {str(e)}")
    
    def get_dimension(self) -> int:
        """Get the dimension of the embeddings."""
        return self.model.get_sentence_embedding_dimension()

class RandomEmbeddingGenerator(BaseEmbeddingGenerator):
    """Random embedding generator for testing."""
    
    def __init__(self, dimension: int = 768):
        """
        Initialize random embedding generator.
        
        Args:
            dimension: Dimension of embeddings
        """
        self.dimension = dimension
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate random embeddings for testing."""
        if not texts:
            return []
        
        embeddings = []
        for _ in texts:
            embedding = np.random.randn(self.dimension)
            # Normalize to unit length
            embedding = embedding / np.linalg.norm(embedding)
            embeddings.append(embedding.tolist())
        
        return embeddings
    
    def get_dimension(self) -> int:
        """Get the dimension of the embeddings."""
        return self.dimension

def create_embedding_generator(config: Dict[str, Any]) -> BaseEmbeddingGenerator:
    """
    Create an embedding generator based on configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Embedding generator instance
    """
    embedding_type = config.get('embedding_type', 'openai').lower()
    
    if embedding_type == 'openai':
        if not config.get('openai_api_key'):
            raise ConfigurationError("OpenAI API key is required for OpenAI embeddings")
        
        return OpenAIEmbeddingGenerator(
            api_key=config['openai_api_key'],
            model=config.get('openai_model', 'text-embedding-ada-002')
        )
    
    elif embedding_type == 'huggingface':
        model_name = config.get('huggingface_model', 'sentence-transformers/all-MiniLM-L6-v2')
        return HuggingFaceEmbeddingGenerator(model_name)
    
    elif embedding_type == 'random':
        return RandomEmbeddingGenerator()
    
    else:
        raise ConfigurationError(f"Unsupported embedding type: {embedding_type}")