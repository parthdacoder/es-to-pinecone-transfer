"""
Custom exceptions for the ES to Pinecone transfer pipeline.
"""

class ESPipelineError(Exception):
    """Base exception for the ES to Pinecone pipeline."""
    pass

class ElasticsearchConnectionError(ESPipelineError):
    """Raised when there's an error connecting to Elasticsearch."""
    pass

class PineconeConnectionError(ESPipelineError):
    """Raised when there's an error connecting to Pinecone."""
    pass

class EmbeddingError(ESPipelineError):
    """Raised when there's an error generating embeddings."""
    pass

class ConfigurationError(ESPipelineError):
    """Raised when there's an error in the pipeline configuration."""
    pass

class BatchProcessingError(ESPipelineError):
    """Raised when there's an error processing a batch of documents."""
    pass