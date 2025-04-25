# Configuration Options

`es-to-pinecone` offers flexible configuration through environment variables or direct code settings.

## Configuration Methods

### 1. Environment Variables (.env file)

Create a `.env` file in your project root:

```ini
# Elasticsearch Configuration
ES_HOST=http://localhost:9200
ES_USERNAME=your_username
ES_PASSWORD=your_password
ES_INDEX=your_index

# Embedding Configuration
EMBEDDING_TYPE=openai
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=text-embedding-ada-002

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_environment
PINECONE_INDEX_NAME=your_index

# Pipeline Configuration
BATCH_SIZE=100
MAX_THREADS=5
FIELDS_TO_EMBED=title,content
METADATA_FIELDS=author,date,url
DEFAULT_NAMESPACE=default
```

### 2. Direct Configuration

```python
config = {
    # Elasticsearch Configuration
    'es_host': 'http://localhost:9200',
    'es_username': 'your_username',
    'es_password': 'your_password',
    'es_index': 'your_index',
    
    # Embedding Configuration
    'embedding_type': 'openai',
    'openai_api_key': 'your_openai_key',
    'openai_model': 'text-embedding-ada-002',
    
    # Pinecone Configuration
    'pinecone_api_key': 'your_pinecone_key',
    'pinecone_environment': 'your_environment',
    'pinecone_index_name': 'your_index',
    
    # Pipeline Configuration
    'batch_size': 100,
    'max_threads': 5,
    'fields_to_embed': ['title', 'content'],
    'metadata_fields': ['author', 'date', 'url'],
    'default_namespace': 'default'
}

pipeline = ElasticsearchToPineconePipeline(config=config)
```

## Configuration Options

### Elasticsearch Options

| Parameter | Environment Variable | Default | Description |
|-----------|---------------------|---------|-------------|
| `es_host` | `ES_HOST` | `http://localhost:9200` | Elasticsearch host URL |
| `es_username` | `ES_USERNAME` | None | Username for Elasticsearch authentication |
| `es_password` | `ES_PASSWORD` | None | Password for Elasticsearch authentication |
| `es_api_key` | `ES_API_KEY` | None | API key for Elasticsearch authentication |
| `es_index` | `ES_INDEX` | None | Elasticsearch index to read documents from |

### Embedding Options

| Parameter | Environment Variable | Default | Description |
|-----------|---------------------|---------|-------------|
| `embedding_type` | `EMBEDDING_TYPE` | `openai` | Type of embedding to use (`openai`, `huggingface`, or `random`) |
| `openai_api_key` | `OPENAI_API_KEY` | None | OpenAI API key (required for OpenAI embeddings) |
| `openai_model` | `OPENAI_MODEL` | `text-embedding-ada-002` | OpenAI embedding model to use |
| `huggingface_model` | `HUGGINGFACE_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | HuggingFace model to use |

### Pinecone Options

| Parameter | Environment Variable | Default | Description |
|-----------|---------------------|---------|-------------|
| `pinecone_api_key` | `PINECONE_API_KEY` | None | Pinecone API key |
| `pinecone_environment` | `PINECONE_ENVIRONMENT` | None | Pinecone environment |
| `pinecone_index_name` | `PINECONE_INDEX_NAME` | None | Pinecone index to write vectors to |
| `default_namespace` | `DEFAULT_NAMESPACE` | `default` | Default namespace in Pinecone |

### Pipeline Options

| Parameter | Environment Variable | Default | Description |
|-----------|---------------------|---------|-------------|
| `batch_size` | `BATCH_SIZE` | `100` | Number of documents to process in each batch |
| `max_threads` | `MAX_THREADS` | `5` | Maximum number of threads to use for processing |
| `fields_to_embed` | `FIELDS_TO_EMBED` | `[]` | Fields from Elasticsearch documents to use for embedding generation |
| `metadata_fields` | `METADATA_FIELDS` | `[]` | Fields to include as metadata in Pinecone |

## Required vs Optional Configuration

**Required Fields:**
- `es_index`
- `pinecone_api_key`
- `pinecone_environment`
- `pinecone_index_name`
- `fields_to_embed`

If `embedding_type` is set to `openai`, then `openai_api_key` is also required.

**Authentication:**
For Elasticsearch authentication, at least one of the following must be provided:
- `es_api_key`
- Both `es_username` and `es_password`
