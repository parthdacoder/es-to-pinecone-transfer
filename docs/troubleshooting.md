# Troubleshooting

This guide addresses common issues you might encounter when using the `es-to-pinecone` package and provides solutions.

## Connection Issues

### Elasticsearch Connection Failures

**Issue**: Unable to connect to Elasticsearch.

**Possible Causes and Solutions**:

1. **Incorrect host URL**:
   - Ensure the `ES_HOST` value is correct, including the protocol (http/https) and port.
   - Try testing the connection with curl: `curl -X GET http://localhost:9200`

2. **Authentication issues**:
   - Verify that `ES_USERNAME` and `ES_PASSWORD` or `ES_API_KEY` are correct.
   - Check if your Elasticsearch instance requires HTTPS.

3. **Network issues**:
   - Check if you can reach the Elasticsearch server from your current environment.
   - Verify firewall settings aren't blocking connections.

4. **SSL/TLS issues**:
   - If using HTTPS, you might need to provide a CA certificate: set `ES_CA_CERT` in your config.

### Pinecone Connection Failures

**Issue**: Unable to connect to Pinecone.

**Possible Causes and Solutions**:

1. **Invalid API key**:
   - Verify your `PINECONE_API_KEY` is correct and still active.
   - Create a new API key if needed.

2. **Environment/region issues**:
   - Ensure `PINECONE_ENVIRONMENT` is set correctly (e.g., 'us-west1-gcp').
   - Check if your Pinecone plan has access to the selected environment.

3. **Rate limiting**:
   - You might be exceeding your Pinecone API rate limits.
   - Try reducing `MAX_THREADS` to limit concurrent requests.

## Embedding Issues

### OpenAI Embedding Failures

**Issue**: Unable to generate embeddings with OpenAI.

**Possible Causes and Solutions**:

1. **API key issues**:
   - Verify your `OPENAI_API_KEY` is correct and has sufficient quota.

2. **Model availability**:
   - Check if the specified `OPENAI_MODEL` is available in your region.
   - Try using a different model, e.g., 'text-embedding-ada-002' or 'text-embedding-3-small'.

3. **Rate limits**:
   - You might be hitting OpenAI's rate limits.
   - Try reducing `BATCH_SIZE` and `MAX_THREADS` to limit concurrent requests.

4. **Input text issues**:
   - Ensure the text being embedded doesn't exceed OpenAI's token limits.
   - Check that the fields specified in `FIELDS_TO_EMBED` exist in your documents.

### HuggingFace Embedding Failures

**Issue**: Unable to generate embeddings with HuggingFace.

**Possible Causes and Solutions**:

1. **Missing dependencies**:
   - Ensure `sentence-transformers` is installed: `pip install sentence-transformers`.

2. **Model download issues**:
   - The first run may take time as it downloads the model.
   - Check your internet connection and available disk space.

3. **Memory issues**:
   - Large models might exceed available RAM.
   - Try using a smaller model or reducing `BATCH_SIZE`.

## Performance Issues

### Pipeline Runs Too Slowly

**Possible Causes and Solutions**:

1. **Thread configuration**:
   - Try increasing `MAX_THREADS` to utilize more CPU cores.
   - However, too many threads might cause API rate limit issues.

2. **Batch size**:
   - Adjust `BATCH_SIZE` - larger batches reduce overhead but use more memory.
   - Finding the optimal batch size often requires experimentation.

3. **Network latency**:
   - If your service is far from Elasticsearch or Pinecone servers, latency can be significant.
   - Consider running your application in the same region as your services.

4. **Embedding generation bottleneck**:
   - Embedding generation is often the slowest part, especially with API-based services.
   - Consider using a local embedding model via HuggingFace for higher throughput.

### Memory Usage Issues

**Possible Causes and Solutions**:

1. **Large documents**:
   - If processing very large documents, reduce `BATCH_SIZE`.
   - Consider pre-filtering documents to include only necessary fields.

2. **Too many threads**:
   - Each thread consumes memory, so reduce `MAX_THREADS` if you encounter memory issues.

3. **HuggingFace models**:
   - Local embedding models consume significant RAM.
   - Use a smaller model or switch to API-based embedding if memory is limited.

## Data-Related Issues

### Missing Fields in Documents

**Issue**: The pipeline fails to process certain fields.

**Possible Causes and Solutions**:

1. **Field doesn't exist**:
   - Verify that fields in `FIELDS_TO_EMBED` and `METADATA_FIELDS` exist in your Elasticsearch documents.
   - Use field mapping to handle renamed fields.

2. **Nested fields**:
   - For nested fields, use dot notation: `parent.child`.
   - Check if your query is correctly returning nested fields.

### No Documents Found

**Issue**: The pipeline reports zero documents to process.

**Possible Causes and Solutions**:

1. **Index name incorrect**:
   - Verify the `ES_INDEX` value matches your Elasticsearch index name.
   - Check if the index exists with: `curl -X GET http://localhost:9200/_cat/indices`.

2. **Query filtering all documents**:
   - If using a custom query, verify it's not too restrictive.
   - Try running without a query first.

3. **Index is empty**:
   - Confirm your index actually contains documents.

### Pinecone Dimension Mismatch

**Issue**: Dimension mismatch errors when upserting to Pinecone.

**Possible Causes and Solutions**:

1. **Index created with wrong dimension**:
   - Pinecone indexes have a fixed dimension.
   - Create a new index with the correct dimension.

2. **Embedding model dimension changed**:
   - Different embedding models produce vectors of different dimensions.
   - Ensure you're using the same model as when you created the index.

## Common Error Messages

### "ElasticsearchConnectionError: Failed to connect to Elasticsearch"

**Solutions**:
- Check your Elasticsearch connection details.
- Verify the Elasticsearch server is running and accessible.
- Check network connectivity and firewall settings.

### "EmbeddingError: Failed to generate embeddings"

**Solutions**:
- Verify API keys for OpenAI or other embedding services.
- Check rate limits and quotas

### "PineconeConnectionError: Failed to initialize Pinecone"

**Solutions**:
- Verify your Pinecone API key is correct.
- Check that the environment and index name are valid.
- Ensure your account has access to the specified environment.
- Verify you haven't exceeded your Pinecone service limits.

### "BatchProcessingError: Failed to process batch"

**Solutions**:
- Look for more specific error messages in the logs.
- Check if document fields match what's specified in your configuration.
- Verify embedding service connectivity.
- Try reducing batch size to identify problematic documents.

### "ConfigurationError: Missing required configuration"

**Solutions**:
- Ensure all required configuration parameters are set.
- Check your .env file format for proper syntax.
- Verify the file path to your .env file if using a custom path.

## Advanced Troubleshooting

### Enabling Debug Logging

To get more detailed log information:

```python
import logging
import es_to_pinecone_transfer

# Set logging level to DEBUG for the package
logging.getLogger('es_to_pinecone_transfer').setLevel(logging.DEBUG)

# Set up a console handler to see the logs
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logging.getLogger('es_to_pinecone_transfer').addHandler(handler)

# Initialize and run the pipeline as usual
pipeline = ElasticsearchToPineconePipeline()
stats = pipeline.run()
```

### Testing Components Individually

If you're having trouble identifying where an issue is occurring, test each component separately:

1. **Test Elasticsearch connection:**

```python
from es_to_pinecone_transfer.elasticsearch_client import ElasticsearchClient

config = {
    'es_host': 'http://localhost:9200',
    'es_username': 'your_username',
    'es_password': 'your_password',
    'es_index': 'your_index'
}

try:
    client = ElasticsearchClient(config)
    count = client.get_document_count()
    print(f"Successfully connected to Elasticsearch. Document count: {count}")
    
    # Test document retrieval
    docs = client.scan_documents(batch_size=5)
    print(f"Retrieved {len(docs)} documents")
    if docs:
        print(f"Sample document fields: {list(docs[0].keys())}")
except Exception as e:
    print(f"Error: {str(e)}")
```

2. **Test embedding generation:**

```python
from es_to_pinecone_transfer.embeddings import create_embedding_generator

config = {
    'embedding_type': 'openai',
    'openai_api_key': 'your_openai_key',
    'openai_model': 'text-embedding-ada-002'
}

try:
    generator = create_embedding_generator(config)
    texts = ["This is a test document."]
    embeddings = generator.generate_embeddings(texts)
    print(f"Successfully generated embeddings. Dimension: {len(embeddings[0])}")
except Exception as e:
    print(f"Error: {str(e)}")
```

3. **Test Pinecone connection:**

```python
from es_to_pinecone_transfer.pinecone_client import PineconeClient

config = {
    'pinecone_api_key': 'your_pinecone_key',
    'pinecone_environment': 'your_environment',
    'pinecone_index_name': 'your_index',
    'embedding_type': 'openai'  # Needed to determine dimension
}

try:
    client = PineconeClient(config)
    stats = client.get_index_stats()
    print(f"Successfully connected to Pinecone. Index stats: {stats}")
except Exception as e:
    print(f"Error: {str(e)}")
```

### Common Compatibility Issues

1. **Elasticsearch version compatibility:**
   - The package is designed to work with Elasticsearch 7.x and 8.x.
   - Different versions might have API differences that affect functionality.
   - Check your Elasticsearch version with `curl -X GET http://localhost:9200`.

2. **Pinecone client version:**
   - The package supports both old and new Pinecone client versions.
   - If you encounter issues, try updating to the latest Pinecone client: `pip install --upgrade pinecone-client`.

3. **OpenAI API changes:**
   - OpenAI occasionally changes their API.
   - For the latest changes, check the OpenAI documentation or update the OpenAI package: `pip install --upgrade openai`.

### Handling Document Size Limitations

1. **Elasticsearch scroll size:**
   - If processing large indices, the scroll timeout might expire.
   - Increase batch size or reduce processing time per batch.

2. **OpenAI token limits:**
   - OpenAI has token limits for their embedding APIs.
   - Consider truncating or chunking large documents.

3. **Pinecone metadata size limits:**
   - Pinecone has size limits for metadata fields.
   - Consider limiting the amount of text in metadata fields.

## System Requirements and Limitations

- **Memory Usage:** The package memory usage depends on batch size, number of threads, and embedding dimension.
- **CPU Usage:** Higher thread counts improve throughput but increase CPU load.
- **Disk Space:** If using HuggingFace, ensure enough disk space for model downloads.
- **Network Bandwidth:** Transferring large volumes of documents requires good network bandwidth.

## Getting Help

If you continue to encounter issues:

1. **Check this documentation for solutions.**
2. **Review the logging output** for specific error messages.
3. **Open an issue on GitHub** with detailed information about your setup and the problem.
4. **Include relevant logs** and configuration (with sensitive information redacted).
