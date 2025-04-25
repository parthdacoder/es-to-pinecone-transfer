"""
ES to Pinecone Transfer Pipeline

A threaded pipeline for transferring documents from Elasticsearch to Pinecone.
"""

__version__ = "0.1.0"

from .pipeline import ElasticsearchToPineconePipeline
from .exceptions import (
    ESPipelineError,
    ElasticsearchConnectionError,
    PineconeConnectionError,
    EmbeddingError,
    ConfigurationError
)

__all__ = [
    "ElasticsearchToPineconePipeline",
    "ESPipelineError",
    "ElasticsearchConnectionError",
    "PineconeConnectionError",
    "EmbeddingError",
    "ConfigurationError"
]