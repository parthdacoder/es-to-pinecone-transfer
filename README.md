# ES to Pinecone Transfer Pipeline

A Python package for transferring documents from Elasticsearch to Pinecone with threading support for faster operations.

## Features

- Transfer documents from Elasticsearch to Pinecone with minimal configuration
- Support for multiple embedding providers (OpenAI, HuggingFace)
- Multi-threaded processing for faster operations
- Configurable batch sizes and field selection
- Progress tracking with tqdm
- Comprehensive error handling

## Installation

```bash
pip install es-to-pinecone-transfer
```

## Quick Start

1. Create a `.env` file with your configuration (see `.env.example` for reference)

2. Use the pipeline directly in your code:

```python
from es_to_pinecone_transfer.pipeline import ElasticsearchToPineconePipeline

# Initialize and run the pipeline
pipeline = ElasticsearchToPineconePipeline()
pipeline.run()
```

3. Or use the command-line interface:

```bash
es-to-pinecone
```

## Configuration

The pipeline can be configured using environment variables. Here are the key settings:

### Elasticsearch Configuration
- `ES_HOST`: Elasticsearch host URL
- `ES_USERNAME`: Elasticsearch username (optional)
- `ES_PASSWORD`: Elasticsearch password (optional)
- `ES_API_KEY`: Elasticsearch API key (optional, preferred over username/password)
- `ES_INDEX`: Source index name

### Embedding Configuration
- `EMBEDDING_TYPE`: Type of embedding to use (openai/huggingface/custom)
- `OPENAI_API_KEY`: OpenAI API key (if using OpenAI embeddings)
- `OPENAI_MODEL`: OpenAI model to use for embeddings
- `HUGGINGFACE_MODEL`: HuggingFace model to use (if using HuggingFace)

### Pinecone Configuration
- `PINECONE_API_KEY`: Pinecone API key
- `PINECONE_ENVIRONMENT`: Pinecone environment
- `PINECONE_INDEX_NAME`: Target Pinecone index name

### Pipeline Configuration
- `BATCH_SIZE`: Number of documents to process in each batch
- `MAX_THREADS`: Maximum number of threads to use
- `FIELDS_TO_EMBED`: Comma-separated list of fields to embed from ES documents
- `METADATA_FIELDS`: Comma-separated list of fields to include as metadata
- `DEFAULT_NAMESPACE`: Pinecone namespace to use

## Advanced Usage

### Custom Field Mapping

```python
from es_to_pinecone_transfer.pipeline import ElasticsearchToPineconePipeline

pipeline = ElasticsearchToPineconePipeline()
pipeline.set_field_mapping({
    'title': 'headline',
    'content': 'body',
    'author': 'writer',
    'timestamp': 'date'
})
pipeline.run()
```

### Progress Callbacks

```python
def on_batch_complete(batch_number, total_batches):
    print(f"Completed batch {batch_number} of {total_batches}")

pipeline = ElasticsearchToPineconePipeline()
pipeline.set_progress_callback(on_batch_complete)
pipeline.run()
```

## Error Handling

The pipeline provides comprehensive error handling:

```python
try:
    pipeline = ElasticsearchToPineconePipeline()
    pipeline.run()
except ElasticsearchConnectionError as e:
    print(f"Elasticsearch connection failed: {e}")
except PineconeConnectionError as e:
    print(f"Pinecone connection failed: {e}")
except EmbeddingError as e:
    print(f"Embedding generation failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.