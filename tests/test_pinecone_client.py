"""
Tests for the Pinecone client with mocking for older pinecone-client API.
"""

import unittest
from unittest.mock import patch, MagicMock, Mock

class TestPineconeClient(unittest.TestCase):
    
    @patch('pinecone.init')
    @patch('pinecone.list_indexes')
    @patch('pinecone.Index')
    def test_client_initialization(self, mock_index, mock_list_indexes, mock_init):
        """Test client initialization when index exists."""
        # Import here to allow mocks to be properly applied
        from es_to_pinecone_transfer.pinecone_client import PineconeClient
        
        # Setup mocks
        mock_list_indexes.return_value = ['test_index']
        mock_index_instance = Mock()
        mock_index.return_value = mock_index_instance
        
        # Configure test
        config = {
            'pinecone_api_key': 'test_key',
            'pinecone_index_name': 'test_index',
            'default_namespace': 'default',
            'embedding_type': 'openai'
        }
        
        # Initialize client
        client = PineconeClient(config)
        
        # Assert expectations
        mock_init.assert_called_once_with(api_key='test_key')
        mock_list_indexes.assert_called_once()
        mock_index.assert_called_once_with('test_index')
        self.assertEqual(client.index, mock_index_instance)
    
    @patch('pinecone.init')
    @patch('pinecone.list_indexes')
    @patch('pinecone.create_index')
    @patch('pinecone.Index')
    def test_client_initialization_create_index(self, mock_index, mock_create_index, 
                                                mock_list_indexes, mock_init):
        """Test client initialization when index needs to be created."""
        # Import here to allow mocks to be properly applied
        from es_to_pinecone_transfer.pinecone_client import PineconeClient
        
        # Setup mocks
        mock_list_indexes.return_value = []
        mock_index_instance = Mock()
        mock_index.return_value = mock_index_instance
        
        # Configure test
        config = {
            'pinecone_api_key': 'test_key',
            'pinecone_index_name': 'test_index',
            'default_namespace': 'default',
            'embedding_type': 'openai'
        }
        
        # Initialize client
        client = PineconeClient(config)
        
        # Assert expectations
        mock_init.assert_called_once_with(api_key='test_key')
        mock_create_index.assert_called_once()
        mock_index.assert_called_once_with('test_index')
    
    @patch('pinecone.init')
    @patch('pinecone.list_indexes')
    @patch('pinecone.Index')
    def test_upsert_vectors(self, mock_index, mock_list_indexes, mock_init):
        """Test upserting vectors."""
        # Import here to allow mocks to be properly applied
        from es_to_pinecone_transfer.pinecone_client import PineconeClient
        
        # Setup mocks
        mock_list_indexes.return_value = ['test_index']
        mock_index_instance = Mock()
        mock_index_instance.upsert.return_value = {'upserted_count': 2}
        mock_index.return_value = mock_index_instance
        
        # Configure test
        config = {
            'pinecone_api_key': 'test_key',
            'pinecone_index_name': 'test_index',
            'default_namespace': 'default',
            'embedding_type': 'openai'
        }
        
        # Initialize client
        client = PineconeClient(config)
        
        # Test data
        vectors = [
            {'id': '1', 'values': [0.1, 0.2], 'metadata': {'field': 'value1'}},
            {'id': '2', 'values': [0.3, 0.4], 'metadata': {'field': 'value2'}}
        ]
        
        # Call method
        result = client.upsert_vectors(vectors)
        
        # Assert expectations
        self.assertEqual(result['upserted_count'], 2)
        mock_index_instance.upsert.assert_called_once()
    
    @patch('pinecone.init')
    @patch('pinecone.list_indexes')
    @patch('pinecone.Index')
    def test_delete_vectors(self, mock_index, mock_list_indexes, mock_init):
        """Test deleting vectors."""
        # Import here to allow mocks to be properly applied
        from es_to_pinecone_transfer.pinecone_client import PineconeClient
        
        # Setup mocks
        mock_list_indexes.return_value = ['test_index']
        mock_index_instance = Mock()
        mock_index.return_value = mock_index_instance
        
        # Configure test
        config = {
            'pinecone_api_key': 'test_key',
            'pinecone_index_name': 'test_index',
            'default_namespace': 'default',
            'embedding_type': 'openai'
        }
        
        # Initialize client
        client = PineconeClient(config)
        
        # Call method
        success = client.delete_vectors(['1', '2'])
        
        # Assert expectations
        self.assertTrue(success)
        mock_index_instance.delete.assert_called_once_with(ids=['1', '2'], namespace='default')
    
    @patch('pinecone.init')
    @patch('pinecone.list_indexes')
    @patch('pinecone.Index')
    def test_query_vectors(self, mock_index, mock_list_indexes, mock_init):
        """Test querying vectors."""
        # Import here to allow mocks to be properly applied
        from es_to_pinecone_transfer.pinecone_client import PineconeClient
        
        # Setup mocks
        mock_list_indexes.return_value = ['test_index']
        mock_index_instance = Mock()
        mock_index_instance.query.return_value = {
            'matches': [
                {'id': '1', 'score': 0.9, 'metadata': {'field': 'value1'}},
                {'id': '2', 'score': 0.8, 'metadata': {'field': 'value2'}}
            ]
        }
        mock_index.return_value = mock_index_instance
        
        # Configure test
        config = {
            'pinecone_api_key': 'test_key',
            'pinecone_index_name': 'test_index',
            'default_namespace': 'default',
            'embedding_type': 'openai'
        }
        
        # Initialize client
        client = PineconeClient(config)
        
        # Call method
        query_vector = [0.1, 0.2]
        matches = client.query_vectors(query_vector, top_k=5)
        
        # Assert expectations
        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0]['id'], '1')
        self.assertEqual(matches[0]['score'], 0.9)
        self.assertIn('metadata', matches[0])
    
    @patch('pinecone.init')
    @patch('pinecone.list_indexes')
    @patch('pinecone.Index')
    def test_get_index_stats(self, mock_index, mock_list_indexes, mock_init):
        """Test getting index stats."""
        # Import here to allow mocks to be properly applied
        from es_to_pinecone_transfer.pinecone_client import PineconeClient
        
        # Setup mocks
        mock_list_indexes.return_value = ['test_index']
        mock_index_instance = Mock()
        mock_index_instance.describe_index_stats.return_value = {
            'dimension': 1536,
            'total_vector_count': 1000,
            'namespaces': {'default': {'vector_count': 1000}}
        }
        mock_index.return_value = mock_index_instance
        
        # Configure test
        config = {
            'pinecone_api_key': 'test_key',
            'pinecone_index_name': 'test_index',
            'default_namespace': 'default',
            'embedding_type': 'openai'
        }
        
        # Initialize client
        client = PineconeClient(config)
        
        # Call method
        stats = client.get_index_stats()
        
        # Assert expectations
        self.assertIn('dimension', stats)
        self.assertIn('total_vector_count', stats)
    
    @patch('pinecone.init')
    @patch('pinecone.list_indexes')
    @patch('pinecone.Index')
    def test_clear_namespace(self, mock_index, mock_list_indexes, mock_init):
        """Test clearing a namespace."""
        # Import here to allow mocks to be properly applied
        from es_to_pinecone_transfer.pinecone_client import PineconeClient
        
        # Setup mocks
        mock_list_indexes.return_value = ['test_index']
        mock_index_instance = Mock()
        mock_index.return_value = mock_index_instance
        
        # Configure test
        config = {
            'pinecone_api_key': 'test_key',
            'pinecone_index_name': 'test_index',
            'default_namespace': 'default',
            'embedding_type': 'openai'
        }
        
        # Initialize client
        client = PineconeClient(config)
        
        # Call method
        success = client.clear_namespace('test_namespace')
        
        # Assert expectations
        self.assertTrue(success)
        mock_index_instance.delete.assert_called_once_with(delete_all=True, namespace='test_namespace')


if __name__ == '__main__':
    unittest.main()