"""
Tests for the main pipeline.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from es_to_pinecone_transfer.pipeline import ElasticsearchToPineconePipeline
from es_to_pinecone_transfer.exceptions import ESPipelineError, ConfigurationError

class TestElasticsearchToPineconePipeline(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'es_host': 'http://localhost:9200',
            'es_index': 'test_index',
            'pinecone_api_key': 'test_key',
            'pinecone_environment': 'test_env',
            'pinecone_index_name': 'test_index',
            'embedding_type': 'random',
            'batch_size': 10,
            'max_threads': 2,
            'fields_to_embed': ['title', 'content'],
            'metadata_fields': ['author', 'timestamp']
        }
    
    @patch('es_to_pinecone_transfer.pipeline.ElasticsearchClient')
    @patch('es_to_pinecone_transfer.pipeline.PineconeClient')
    @patch('es_to_pinecone_transfer.pipeline.create_embedding_generator')
    def test_pipeline_initialization(self, mock_embedding, mock_pinecone, mock_es):
        """Test pipeline initialization."""
        pipeline = ElasticsearchToPineconePipeline(config=self.config)
        
        # Check clients were initialized
        mock_es.assert_called_once_with(self.config)
        mock_pinecone.assert_called_once_with(self.config)
        mock_embedding.assert_called_once_with(self.config)
        
        # Check config values were set
        self.assertEqual(pipeline.batch_size, 10)
        self.assertEqual(pipeline.max_threads, 2)
    
    @patch('es_to_pinecone_transfer.pipeline.ElasticsearchClient')
    @patch('es_to_pinecone_transfer.pipeline.PineconeClient')
    @patch('es_to_pinecone_transfer.pipeline.create_embedding_generator')
    def test_process_batch(self, mock_embedding, mock_pinecone, mock_es):
        """Test batch processing."""
        # Setup mocks
        mock_embedding_instance = Mock()
        mock_embedding_instance.generate_embeddings.return_value = [[0.1, 0.2], [0.3, 0.4]]
        mock_embedding.return_value = mock_embedding_instance
        
        # Create pipeline
        pipeline = ElasticsearchToPineconePipeline(config=self.config)
        
        # Test documents
        documents = [
            {'_id': '1', 'title': 'Test 1', 'content': 'Content 1', 'author': 'Author 1'},
            {'_id': '2', 'title': 'Test 2', 'content': 'Content 2', 'author': 'Author 2'}
        ]
        
        # Process batch
        vectors = pipeline._process_batch(documents)
        
        # Assertions
        self.assertEqual(len(vectors), 2)
        self.assertEqual(vectors[0]['id'], '1')
        self.assertEqual(vectors[0]['values'], [0.1, 0.2])
        self.assertIn('author', vectors[0]['metadata'])
    
    @patch('es_to_pinecone_transfer.pipeline.ElasticsearchClient')
    @patch('es_to_pinecone_transfer.pipeline.PineconeClient')
    @patch('es_to_pinecone_transfer.pipeline.create_embedding_generator')
    def test_run_pipeline(self, mock_embedding, mock_pinecone, mock_es):
        """Test running the full pipeline."""
        # Setup mocks
        mock_es_instance = Mock()
        mock_es_instance.get_document_count.return_value = 100
        mock_es_instance.scan_documents.return_value = [
            {'_id': str(i), 'title': f'Test {i}', 'content': f'Content {i}'} 
            for i in range(100)
        ]
        mock_es.return_value = mock_es_instance
        
        mock_pinecone_instance = Mock()
        mock_pinecone_instance.upsert_vectors.return_value = {'upserted_count': 10}
        mock_pinecone.return_value = mock_pinecone_instance
        
        mock_embedding_instance = Mock()
        mock_embedding_instance.generate_embeddings.return_value = [[0.1, 0.2]] * 10
        mock_embedding.return_value = mock_embedding_instance
        
        # Create and run pipeline
        pipeline = ElasticsearchToPineconePipeline(config=self.config)
        stats = pipeline.run()
        
        # Assertions
        self.assertEqual(stats['processed'], 100)
        self.assertEqual(stats['upserted'], 100)
        self.assertEqual(stats['failed'], 0)
    
    @patch('es_to_pinecone_transfer.pipeline.validate_config')
    def test_invalid_config(self, mock_validate):
        """Test pipeline with invalid configuration."""
        mock_validate.side_effect = ConfigurationError("Invalid config")
        
        with self.assertRaises(ConfigurationError):
            ElasticsearchToPineconePipeline(config={})
    
    def test_field_mapping(self):
        """Test field mapping functionality."""
        with patch('es_to_pinecone_transfer.pipeline.ElasticsearchClient'), \
             patch('es_to_pinecone_transfer.pipeline.PineconeClient'), \
             patch('es_to_pinecone_transfer.pipeline.create_embedding_generator'):
            
            pipeline = ElasticsearchToPineconePipeline(config=self.config)
            
            mapping = {
                'title': 'headline',
                'content': 'body'
            }
            pipeline.set_field_mapping(mapping)
            self.assertEqual(pipeline.field_mapping, mapping)
    
    def test_progress_callback(self):
        """Test progress callback functionality."""
        with patch('es_to_pinecone_transfer.pipeline.ElasticsearchClient'), \
             patch('es_to_pinecone_transfer.pipeline.PineconeClient'), \
             patch('es_to_pinecone_transfer.pipeline.create_embedding_generator'):
            
            pipeline = ElasticsearchToPineconePipeline(config=self.config)
            
            callback = Mock()
            pipeline.set_progress_callback(callback)
            self.assertEqual(pipeline.progress_callback, callback)

if __name__ == '__main__':
    unittest.main()