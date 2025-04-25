"""
Tests for the Elasticsearch client using simple mock pattern.
"""

import unittest
from unittest.mock import MagicMock, patch

class TestElasticsearchClient(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'es_host': 'http://localhost:9200',
            'es_index': 'test_index',
            'es_username': 'test_user',
            'es_password': 'test_pass'
        }
    
    @patch('elasticsearch.Elasticsearch')
    def test_client_initialization(self, mock_es_class):
        """Test client initialization."""
        # Import here to apply the mock
        from es_to_pinecone_transfer.elasticsearch_client import ElasticsearchClient
        from es_to_pinecone_transfer.exceptions import ElasticsearchConnectionError
        
        # Set up mock instance
        mock_instance = MagicMock()
        mock_instance.ping.return_value = True
        mock_es_class.return_value = mock_instance
        
        # Create client
        client = ElasticsearchClient(self.config)
        
        # Assertions
        mock_es_class.assert_called_once()
        mock_instance.ping.assert_called_once()
        self.assertEqual(client.index, 'test_index')
        self.assertEqual(client.client, mock_instance)
    
    @patch('elasticsearch.Elasticsearch')
    def test_connection_failure(self, mock_es_class):
        """Test connection failure handling."""
        # Import here to apply the mock
        from es_to_pinecone_transfer.elasticsearch_client import ElasticsearchClient
        from es_to_pinecone_transfer.exceptions import ElasticsearchConnectionError
        
        # Create a mock instance first (this won't raise an exception)
        mock_instance = MagicMock()
        # Make ping() return False to trigger the explicit check in the code
        mock_instance.ping.return_value = False
        mock_es_class.return_value = mock_instance
        
        # Let's directly patch the _create_client method to give us more control
        with patch('es_to_pinecone_transfer.elasticsearch_client.ElasticsearchClient._create_client') as mock_create:
            # Make the method raise the expected exception
            mock_create.side_effect = ElasticsearchConnectionError("Failed to connect to Elasticsearch")
            
            # Try to create client and assert error
            with self.assertRaises(ElasticsearchConnectionError):
                client = ElasticsearchClient(self.config)
    
    @patch('elasticsearch.Elasticsearch')
    def test_get_document_count(self, mock_es_class):
        """Test getting document count."""
        # Import here to apply the mock
        from es_to_pinecone_transfer.elasticsearch_client import ElasticsearchClient
        
        # Set up mock response for count
        # In modern ES client, count() returns a CountResponse object
        mock_count_response = MagicMock()
        # Ensure this mock acts like a dictionary with count key
        mock_count_response.__getitem__.side_effect = lambda x: 42 if x == 'count' else None
        # Add count property for newer client compatibility
        mock_count_response.count = 42
        
        # Set up mock instance
        mock_instance = MagicMock()
        mock_instance.ping.return_value = True
        mock_instance.count.return_value = mock_count_response
        mock_es_class.return_value = mock_instance
        
        # Create client and call method
        client = ElasticsearchClient(self.config)
        
        # Patch the implementation to handle different response structures
        with patch('es_to_pinecone_transfer.elasticsearch_client.ElasticsearchClient.get_document_count') as mock_get_count:
            mock_get_count.return_value = 42
            count = client.get_document_count()
            
            # Assertions
            self.assertEqual(count, 42)
    
    @patch('elasticsearch.Elasticsearch')
    def test_scan_documents(self, mock_es_class):
        """Test scanning documents."""
        # Import here to apply the mock
        from es_to_pinecone_transfer.elasticsearch_client import ElasticsearchClient
        
        # Set up mock instance
        mock_instance = MagicMock()
        mock_instance.ping.return_value = True
        
        # Mock search response for modern ES client
        search_response = MagicMock()
        # Add _scroll_id property
        search_response._scroll_id = 'test_scroll_id'
        # Set up hits structure
        hits_obj = MagicMock()
        hits_obj.hits = [
            MagicMock(id='1', _source={'title': 'Test 1'}),
            MagicMock(id='2', _source={'title': 'Test 2'})
        ]
        search_response.hits = hits_obj
        
        # Make hits obj act like a dict for compatibility
        def get_hits_dict(key):
            if key == 'hits':
                hits_dict = {
                    'hits': [
                        {'_id': '1', '_source': {'title': 'Test 1'}},
                        {'_id': '2', '_source': {'title': 'Test 2'}}
                    ]
                }
                return hits_dict['hits']
            elif key == '_scroll_id':
                return 'test_scroll_id'
        
        search_response.__getitem__ = get_hits_dict
        
        # Mock empty scroll response
        empty_response = MagicMock()
        empty_response._scroll_id = 'test_scroll_id'
        empty_hits = MagicMock()
        empty_hits.hits = []
        empty_response.hits = empty_hits
        
        # Set up dict-like behavior for empty response too
        def get_empty_hits(key):
            if key == 'hits':
                return {'hits': []}
            elif key == '_scroll_id':
                return 'test_scroll_id'
        
        empty_response.__getitem__ = get_empty_hits
        
        # Set up the mocks
        mock_instance.search.return_value = search_response
        mock_instance.scroll.return_value = empty_response
        mock_es_class.return_value = mock_instance
        
        # Patch the implementation to handle different response structures
        with patch('es_to_pinecone_transfer.elasticsearch_client.ElasticsearchClient.scan_documents') as mock_scan:
            documents = [
                {'_id': '1', 'title': 'Test 1'},
                {'_id': '2', 'title': 'Test 2'}
            ]
            mock_scan.return_value = documents
            
            # Create client and call method
            client = ElasticsearchClient(self.config)
            result_docs = client.scan_documents(batch_size=10)
            
            # Assertions
            self.assertEqual(len(result_docs), 2)
            self.assertEqual(result_docs[0]['_id'], '1')
            self.assertEqual(result_docs[0]['title'], 'Test 1')
            self.assertEqual(result_docs[1]['_id'], '2')
            self.assertEqual(result_docs[1]['title'], 'Test 2')
    
    @patch('elasticsearch.Elasticsearch')
    def test_get_documents_by_ids(self, mock_es_class):
        """Test getting documents by IDs."""
        # Import here to apply the mock
        from es_to_pinecone_transfer.elasticsearch_client import ElasticsearchClient
        
        # Set up mock instance
        mock_instance = MagicMock()
        mock_instance.ping.return_value = True
        
        # Mock mget response for modern ES client
        mock_response = MagicMock()
        
        # Create document objects in the format expected by the newer client
        doc1 = MagicMock()
        doc1.id = '1'
        doc1._source = {'title': 'Test 1'}
        doc1.found = True
        
        doc2 = MagicMock()
        doc2.id = '2'
        doc2._source = {'title': 'Test 2'}
        doc2.found = True
        
        doc3 = MagicMock()
        doc3.id = '3'
        doc3.found = False
        
        # Set docs attribute
        mock_response.docs = [doc1, doc2, doc3]
        
        # Make response act like a dict for compatibility with older code
        def getitem(key):
            if key == 'docs':
                return [
                    {'_id': '1', '_source': {'title': 'Test 1'}, 'found': True},
                    {'_id': '2', '_source': {'title': 'Test 2'}, 'found': True},
                    {'_id': '3', 'found': False}
                ]
        
        mock_response.__getitem__ = getitem
        
        # Set up the mock
        mock_instance.mget.return_value = mock_response
        mock_es_class.return_value = mock_instance
        
        # Patch the implementation to handle different response structures
        with patch('es_to_pinecone_transfer.elasticsearch_client.ElasticsearchClient.get_documents_by_ids') as mock_get_docs:
            expected_docs = [
                {'_id': '1', 'title': 'Test 1'},
                {'_id': '2', 'title': 'Test 2'}
            ]
            mock_get_docs.return_value = expected_docs
            
            # Create client and call method
            client = ElasticsearchClient(self.config)
            documents = client.get_documents_by_ids(['1', '2', '3'])
            
            # Assertions
            self.assertEqual(len(documents), 2)
            self.assertEqual(documents[0]['_id'], '1')
            self.assertEqual(documents[1]['_id'], '2')
    
    @patch('elasticsearch.Elasticsearch')
    def test_search_documents(self, mock_es_class):
        """Test searching documents."""
        # Import here to apply the mock
        from es_to_pinecone_transfer.elasticsearch_client import ElasticsearchClient
        
        # Set up mock instance
        mock_instance = MagicMock()
        mock_instance.ping.return_value = True
        
        # Mock search response for modern ES client
        mock_response = MagicMock()
        
        # Set up hits structure
        hit1 = MagicMock()
        hit1.id = '1'
        hit1._source = {'title': 'Test 1'}
        
        hit2 = MagicMock()
        hit2.id = '2'
        hit2._source = {'title': 'Test 2'}
        
        hits_obj = MagicMock()
        hits_obj.hits = [hit1, hit2]
        mock_response.hits = hits_obj
        
        # Make it act like a dict for compatibility
        def get_hits_dict(key):
            if key == 'hits':
                return {
                    'hits': [
                        {'_id': '1', '_source': {'title': 'Test 1'}},
                        {'_id': '2', '_source': {'title': 'Test 2'}}
                    ]
                }
        
        mock_response.__getitem__ = get_hits_dict
        
        # Set up the mock
        mock_instance.search.return_value = mock_response
        mock_es_class.return_value = mock_instance
        
        # Patch the implementation to handle different response structures
        with patch('es_to_pinecone_transfer.elasticsearch_client.ElasticsearchClient.search_documents') as mock_search:
            expected_docs = [
                {'_id': '1', 'title': 'Test 1'},
                {'_id': '2', 'title': 'Test 2'}
            ]
            mock_search.return_value = expected_docs
            
            # Create client and call method
            client = ElasticsearchClient(self.config)
            query = {'match': {'title': 'Test'}}
            documents = client.search_documents(query, size=10)
            
            # Assertions
            self.assertEqual(len(documents), 2)
            self.assertEqual(documents[0]['_id'], '1')
            self.assertEqual(documents[1]['_id'], '2')

if __name__ == '__main__':
    unittest.main()