# ES to Pinecone Documentation

A comprehensive guide to using the `es-to-pinecone` package.

## Overview

`es-to-pinecone` is a Python package that provides a scalable solution for transferring documents from Elasticsearch to Pinecone with vector embeddings. This tool bridges the gap between traditional search engines and vector databases, enabling semantic search capabilities.

## Key Features

- **Elasticsearch Integration**: Connect to and extract documents from Elasticsearch indices
- **Vector Embeddings**: Generate embeddings using OpenAI, HuggingFace, or random vectors for testing
- **Pinecone Upload**: Upload documents with their vector embeddings to Pinecone
- **Multi-threading**: Process documents in parallel for faster transfers
- **Progress Tracking**: Monitor transfer progress with callbacks
- **Flexible Configuration**: Configure through environment variables or directly in code

## Installation

```bash
pip install es-to-pinecone
```

## Quick Start

```python
from es_to_pinecone_transfer.pipeline import ElasticsearchToPineconePipeline

# Initialize the pipeline (reads from .env file)
pipeline = ElasticsearchToPineconePipeline()

# Run the pipeline
stats = pipeline.run()

print(f"Processed: {stats['processed']} documents")
print(f"Upserted: {stats['upserted']} documents")
print(f"Failed: {stats['failed']} documents")
```

## Next Steps

- [Configuration Options](configuration.md): Learn about all available configuration options
- [Usage Examples](examples.md): See detailed examples for common use cases
- [API Reference](api.md): View the complete API documentation
- [Troubleshooting](troubleshooting.md): Solutions for common issues
