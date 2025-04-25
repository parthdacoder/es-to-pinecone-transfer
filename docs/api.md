# API Reference

This page provides detailed documentation for the main classes and functions in the `es-to-pinecone` package.

## ElasticsearchToPineconePipeline

The main class for transferring documents from Elasticsearch to Pinecone.

### Constructor

```python
ElasticsearchToPineconePipeline(config=None, env_path=None)
```

**Parameters:**
- `config` (dict, optional): Configuration dictionary. If not provided, configuration is loaded from environment variables.
- `env_path` (str, optional): Path to .env file. If not provided, looks for .env in the current directory.

### Methods

#### `run`

```python
run(query=None, dry_run=False)
```

Runs the pipeline to transfer documents from Elasticsearch to Pinecone.

**Parameters:**
- `query` (dict, optional): Elasticsearch query to filter documents.
- `dry_run` (bool, optional): If True, processes documents but doesn't upsert to Pinecone.

**Returns:**
- dict: Dictionary with transfer statistics:
  - `processed`: Number of documents processed
  - `upserted`: Number of documents upserted to Pinecone
  - `failed`: Number of documents that failed processing
  - `total_documents`: Total number of documents in the Elasticsearch index
  - `success_rate`: Percentage of successfully processed documents

#### `set_progress_callback`

```python
set_progress_callback(callback)
```

Sets a callback function for progress updates.

**Parameters:**
- `callback`: Function taking `(current_batch, total_batches)` parameters.

#### `set_field_mapping`

```python
set_field_mapping(mapping)
```

Sets field mapping for document processing.

**Parameters:**
- `mapping`: Dictionary mapping source fields to target fields.

## ElasticsearchClient

Client for interacting with Elasticsearch.

### Constructor

```python
ElasticsearchClient(config)
```

**Parameters:**
- `config` (dict): Configuration dictionary with Elasticsearch connection details.

### Methods

#### `get_document_count`

```python
get_document_count()
```

Gets the total number of documents in the index.

**Returns:**
- int: Number of documents in the index.

#### `scan_documents`

```python
scan_documents(batch_size=100, query=None, fields=None)
```

Scans through documents in the index with pagination.

**Parameters:**
- `batch_size` (int, optional): Number of documents per batch.
- `query` (dict, optional): Elasticsearch query.
- `fields` (list, optional): List of fields to retrieve.

**Returns:**
- list: List of documents.

#### `get_documents_by_ids`

```python
get_documents_by_ids(doc_ids, fields=None)
```

Gets documents by IDs.

**Parameters:**
- `doc_ids` (list): List of document IDs.
- `fields` (list, optional): List of fields to retrieve.

**Returns:**
- list: List of documents.

#### `search_documents`

```python
search_documents(query, size=100, fields=None)
```

Searches for documents using a query.

**Parameters:**
- `query` (dict): Elasticsearch query.
- `size` (int, optional): Maximum number of documents to return.
- `fields` (list, optional): List of fields to retrieve.

**Returns:**
- list: List of documents.

## PineconeClient

Client for interacting with Pinecone.

### Constructor

```python
PineconeClient(config)
```

**Parameters:**
- `config` (dict): Configuration dictionary with Pinecone connection details.

### Methods

#### `upsert_vectors`

```python
upsert_vectors(vectors, namespace=None)
```

Upserts vectors to Pinecone.

**Parameters:**
- `vectors` (list): List of vector dictionaries with id, values, and metadata.
- `namespace` (str, optional): Namespace to use.

**Returns:**
- dict: Dictionary with upsert statistics.

#### `delete_vectors`

```python
delete_vectors(ids, namespace=None)
```

Deletes vectors from Pinecone.

**Parameters:**
- `ids` (list): List of vector IDs to delete.
- `namespace` (str, optional): Namespace.

**Returns:**
- bool: True if successful.

#### `query_vectors`

```python
query_vectors(vector, top_k=10, namespace=None, include_metadata=True)
```

Queries vectors from Pinecone.

**Parameters:**
- `vector` (list): Query vector.
- `top_k` (int, optional): Number of results to return.
- `namespace` (str, optional): Namespace.
- `include_metadata` (bool, optional): Whether to include metadata in results.

**Returns:**
- list: List of matches.

#### `get_index_stats`

```python
get_index_stats()
```

Gets statistics about the Pinecone index.

**Returns:**
- dict: Dictionary with index statistics.

#### `clear_namespace`

```python
clear_namespace(namespace=None)
```

Clears all vectors in a namespace.

**Parameters:**
- `namespace` (str, optional): Namespace to clear.

**Returns:**
- bool: True if successful.

## Embedding Generators

### BaseEmbeddingGenerator

Abstract base class for embedding generators.

### OpenAIEmbeddingGenerator

```python
OpenAIEmbeddingGenerator(api_key, model="text-embedding-ada-002")
```

**Parameters:**
- `api_key` (str): OpenAI API key.
- `model` (str, optional): Model to use for embeddings.

### HuggingFaceEmbeddingGenerator

```python
HuggingFaceEmbeddingGenerator(model_name="sentence-transformers/all-MiniLM-L6-v2")
```

**Parameters:**
- `model_name` (str, optional): HuggingFace model to use.

### RandomEmbeddingGenerator

```python
RandomEmbeddingGenerator(dimension=768)
```

**Parameters:**
- `dimension` (int, optional): Dimension of embeddings.

### create_embedding_generator

```python
create_embedding_generator(config)
```

Creates an embedding generator based on configuration.

**Parameters:**
- `config` (dict): Configuration dictionary.

**Returns:**
- BaseEmbeddingGenerator: Embedding generator instance.
