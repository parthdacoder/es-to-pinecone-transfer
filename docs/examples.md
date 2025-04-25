# Usage Examples

This page provides comprehensive examples of how to use the `es-to-pinecone` package for different scenarios.

## Basic Usage

The simplest way to use the package is to create a `.env` file with your configuration and run the pipeline:

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

## Using a Dry Run First

It's often a good idea to perform a dry run before the actual transfer:

```python
from es_to_pinecone_transfer.pipeline import ElasticsearchToPineconePipeline

# Initialize the pipeline
pipeline = ElasticsearchToPineconePipeline()

# Run a dry run first (doesn't write to Pinecone)
print("Running dry run...")
stats = pipeline.run(dry_run=True)
print(f"Would transfer {stats['processed']} documents")

# Confirm with user
proceed = input("Proceed with actual transfer? (y/n): ")
if proceed.lower() == 'y':
    # Run the actual transfer
    print("Running transfer...")
    stats = pipeline.run()
    print(f"Transfer complete!")
    print(f"Processed: {stats['processed']} documents")
    print(f"Upserted: {stats['upserted']} documents")
    print(f"Failed: {stats['failed']} documents")
else:
    print("Transfer aborted")
```

## Custom Configuration

You can provide a custom configuration directly:

```python
from es_to_pinecone_transfer.pipeline import ElasticsearchToPineconePipeline

# Custom configuration
config = {
    # Elasticsearch Configuration
    'es_host': 'http://localhost:9200',
    'es_username': 'elastic',
    'es_password': 'changeme',
    'es_index': 'blog_posts',
    
    # Embedding Configuration
    'embedding_type': 'openai',
    'openai_api_key': 'your-openai-api-key',
    'openai_model': 'text-embedding-ada-002',
    
    # Pinecone Configuration
    'pinecone_api_key': 'your-pinecone-api-key',
    'pinecone_environment': 'us-west1-gcp',
    'pinecone_index_name': 'blog-embeddings',
    
    # Pipeline Configuration
    'batch_size': 50,
    'max_threads': 4,
    'fields_to_embed': ['title', 'content'],
    'metadata_fields': ['author', 'published_date', 'categories', 'url']
}

# Initialize the pipeline with custom config
pipeline = ElasticsearchToPineconePipeline(config=config)

# Run the pipeline
stats = pipeline.run()
```

## Using HuggingFace Embeddings

To use HuggingFace embeddings instead of OpenAI:

```python
from es_to_pinecone_transfer.pipeline import ElasticsearchToPineconePipeline

# Initialize with HuggingFace embeddings
config = {
    # Elasticsearch and Pinecone configs...
    
    # Embedding Configuration
    'embedding_type': 'huggingface',
    'huggingface_model': 'sentence-transformers/all-MiniLM-L6-v2',
    
    # Other configs...
}

pipeline = ElasticsearchToPineconePipeline(config=config)
stats = pipeline.run()
```

## Filtering Documents with a Query

You can use an Elasticsearch query to filter which documents to transfer:

```python
from es_to_pinecone_transfer.pipeline import ElasticsearchToPineconePipeline

# Initialize the pipeline
pipeline = ElasticsearchToPineconePipeline()

# Define a query to filter documents
query = {
    "bool": {
        "must": [
            {"match": {"status": "published"}},
            {"range": {"published_date": {"gte": "2023-01-01"}}}
        ]
    }
}

# Run the pipeline with the query
stats = pipeline.run(query=query)
```

## Adding a Progress Callback

You can add a progress callback to track the progress of the transfer:

```python
from es_to_pinecone_transfer.pipeline import ElasticsearchToPineconePipeline
import time

# Initialize the pipeline
pipeline = ElasticsearchToPineconePipeline()

# Define a progress callback
start_time = time.time()
def progress_callback(current_batch, total_batches):
    elapsed = time.time() - start_time
    percent = (current_batch / total_batches) * 100
    remaining = (elapsed / current_batch) * (total_batches - current_batch) if current_batch > 0 else 0
    
    print(f"Progress: {current_batch}/{total_batches} ({percent:.2f}%)")
    print(f"Elapsed time: {elapsed:.2f}s, Estimated time remaining: {remaining:.2f}s")

# Set the progress callback
pipeline.set_progress_callback(progress_callback)

# Run the pipeline
stats = pipeline.run()
```

## Field Mapping

You can map fields from Elasticsearch to different names in Pinecone:

```python
from es_to_pinecone_transfer.pipeline import ElasticsearchToPineconePipeline

# Initialize the pipeline
pipeline = ElasticsearchToPineconePipeline()

# Set field mapping
field_mapping = {
    'title': 'document_title',
    'content': 'document_content',
    'author.name': 'author_name',
    'author.email': 'author_email'
}

pipeline.set_field_mapping(field_mapping)

# Run the pipeline
stats = pipeline.run()
```

## Complete Example with Error Handling

Here's a more complete example with error handling:

```python
import os
import logging
from dotenv import load_dotenv
from es_to_pinecone_transfer.pipeline import ElasticsearchToPineconePipeline
from es_to_pinecone_transfer.exceptions import ESPipelineError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

try:
    # Initialize the pipeline
    pipeline = ElasticsearchToPineconePipeline()
    
    # Define a progress callback
    def progress_callback(current_batch, total_batches):
        percent = (current_batch / total_batches) * 100
        logger.info(f"Progress: {current_batch}/{total_batches} ({percent:.2f}%)")
    
    # Set the progress callback
    pipeline.set_progress_callback(progress_callback)
    
    # Define a query to filter documents (optional)
    query = {
        "bool": {
            "must": {"match": {"document_type": "article"}}
        }
    }
    
    # Run a dry run first
    logger.info("Starting dry run...")
    dry_run_stats = pipeline.run(query=query, dry_run=True)
    logger.info(f"Dry run completed. Would process {dry_run_stats['processed']} documents.")
    
    # Run the actual transfer
    logger.info("Starting actual transfer...")
    stats = pipeline.run(query=query)
    
    # Log the results
    logger.info("Transfer completed successfully!")
    logger.info(f"Total documents: {stats['total_documents']}")
    logger.info(f"Processed: {stats['processed']}")
    logger.info(f"Upserted: {stats['upserted']}")
    logger.info(f"Failed: {stats['failed']}")
    logger.info(f"Success rate: {stats['success_rate']:.2f}%")
    
except ESPipelineError as e:
    logger.error(f"Pipeline error: {str(e)}")
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
```

## Command Line Usage

The package also includes a command-line interface:

```bash
# Basic usage
es-to-pinecone

# With options
es-to-pinecone --env /path/to/.env --dry-run --query '{"match": {"type": "article"}}'
```

## Getting Index Statistics from Pinecone

```python
from es_to_pinecone_transfer.pipeline import ElasticsearchToPineconePipeline

# Initialize the pipeline
pipeline = ElasticsearchToPineconePipeline()

# Get Pinecone index statistics
stats = pipeline.pinecone_client.get_index_stats()

print(f"Total vectors: {stats.get('total_vector_count', 0)}")
print(f"Dimension: {stats.get('dimension', 0)}")

# Print namespace statistics
if 'namespaces' in stats:
    for namespace, ns_stats in stats['namespaces'].items():
        print(f"Namespace '{namespace}': {ns_stats.get('vector_count', 0)} vectors")
```

## Querying Vectors in Pinecone

```python
from es_to_pinecone_transfer.pipeline import ElasticsearchToPineconePipeline
from es_to_pinecone_transfer.embeddings import create_embedding_generator

# Initialize the pipeline
pipeline = ElasticsearchToPineconePipeline()

# Get the embedding generator
embedding_generator = create_embedding_generator(pipeline.config)

# Generate an embedding for a query
query_text = "What is machine learning?"
query_embedding = embedding_generator.generate_embeddings([query_text])[0]

# Query Pinecone
results = pipeline.pinecone_client.query_vectors(
    vector=query_embedding,
    top_k=5,
    include_metadata=True
)

# Print results
for i, match in enumerate(results):
    print(f"{i+1}. ID: {match['id']}, Score: {match['score']}")
    if 'metadata' in match:
        # Print title if available
        if 'title' in match['metadata']:
            print(f"   Title: {match['metadata']['title']}")
        # Print a snippet of the text if available
        if 'original_text' in match['metadata']:
            text = match['metadata']['original_text']
            print(f"   Text: {text[:100]}...")
    print("")
```
