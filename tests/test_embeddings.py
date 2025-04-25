"""
Tests for the embedding generators.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import sys
from es_to_pinecone_transfer.embeddings import (
    OpenAIEmbeddingGenerator,
    HuggingFaceEmbeddingGenerator,
    RandomEmbeddingGenerator,
    create_embedding_generator
)
from es_to_pinecone_transfer.exceptions import EmbeddingError, ConfigurationError

class TestOpenAIEmbeddingGenerator(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key"
        self.model = "text-embedding-ada-002"
    
    @patch('openai.api_key', new='test_api_key')
    @patch('openai.embeddings.create')
    def test_generate_embeddings(self, mock_create):
        """Test generating embeddings with OpenAI."""
        # Mock the response data structure that matches current OpenAI API
        mock_data = [
            MagicMock(embedding=[0.1, 0.2, 0.3]),
            MagicMock(embedding=[0.4, 0.5, 0.6])
        ]
        mock_response = MagicMock(data=mock_data)
        mock_create.return_value = mock_response
        
        generator = OpenAIEmbeddingGenerator(self.api_key, self.model)
        embeddings = generator.generate_embeddings(["text1", "text2"])
        
        self.assertEqual(len(embeddings), 2)
        self.assertEqual(embeddings[0], [0.1, 0.2, 0.3])
        self.assertEqual(embeddings[1], [0.4, 0.5, 0.6])
        
        # Verify the correct model and input were used
        mock_create.assert_called_once_with(
            model=self.model,
            input=["text1", "text2"]
        )
    
    @patch('openai.api_key', new='test_api_key')
    @patch('openai.embeddings.create')
    def test_generate_embeddings_error(self, mock_create):
        """Test error handling in OpenAI embedding generation."""
        mock_create.side_effect = Exception("API Error")
        
        generator = OpenAIEmbeddingGenerator(self.api_key, self.model)
        
        with self.assertRaises(EmbeddingError):
            generator.generate_embeddings(["text1", "text2"])
    
    def test_get_dimension(self):
        """Test getting embedding dimension."""
        generator = OpenAIEmbeddingGenerator(self.api_key, self.model)
        self.assertEqual(generator.get_dimension(), 1536)
        
        generator = OpenAIEmbeddingGenerator(self.api_key, "text-embedding-3-large")
        self.assertEqual(generator.get_dimension(), 3072)
    
    @patch('openai.api_key', new='test_api_key')
    @patch('openai.embeddings.create')
    def test_empty_text_list(self, mock_create):
        """Test handling empty text list."""
        generator = OpenAIEmbeddingGenerator(self.api_key, self.model)
        embeddings = generator.generate_embeddings([])
        
        self.assertEqual(embeddings, [])
        mock_create.assert_not_called()

# Skip HuggingFace tests if sentence-transformers is not installed
try:
    import sentence_transformers
    SKIP_HF_TESTS = False
except ImportError:
    SKIP_HF_TESTS = True

@unittest.skipIf(SKIP_HF_TESTS, "sentence-transformers not installed")
class TestHuggingFaceEmbeddingGenerator(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
    
    @patch('sentence_transformers.SentenceTransformer')
    def test_generate_embeddings(self, mock_st):
        """Test generating embeddings with HuggingFace."""
        # Mock model
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1, 0.2], [0.3, 0.4]])
        mock_st.return_value = mock_model
        
        generator = HuggingFaceEmbeddingGenerator(self.model_name)
        embeddings = generator.generate_embeddings(["text1", "text2"])
        
        self.assertEqual(len(embeddings), 2)
        self.assertEqual(embeddings[0], [0.1, 0.2])
        self.assertEqual(embeddings[1], [0.3, 0.4])
        
        mock_model.encode.assert_called_once_with(["text1", "text2"], convert_to_numpy=True)
    
    @patch('sentence_transformers.SentenceTransformer')
    def test_get_dimension(self, mock_st):
        """Test getting embedding dimension."""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_st.return_value = mock_model
        
        generator = HuggingFaceEmbeddingGenerator(self.model_name)
        self.assertEqual(generator.get_dimension(), 384)

class TestRandomEmbeddingGenerator(unittest.TestCase):
    
    def test_generate_embeddings(self):
        """Test generating random embeddings."""
        generator = RandomEmbeddingGenerator(dimension=10)
        embeddings = generator.generate_embeddings(["text1", "text2", "text3"])
        
        self.assertEqual(len(embeddings), 3)
        self.assertEqual(len(embeddings[0]), 10)
        
        # Check normalization
        for embedding in embeddings:
            norm = np.linalg.norm(embedding)
            self.assertAlmostEqual(norm, 1.0, places=5)
    
    def test_get_dimension(self):
        """Test getting embedding dimension."""
        generator = RandomEmbeddingGenerator(dimension=15)
        self.assertEqual(generator.get_dimension(), 15)
    
    def test_empty_text_list(self):
        """Test handling empty text list."""
        generator = RandomEmbeddingGenerator()
        embeddings = generator.generate_embeddings([])
        self.assertEqual(embeddings, [])

class TestCreateEmbeddingGenerator(unittest.TestCase):
    
    @patch('es_to_pinecone_transfer.embeddings.OpenAIEmbeddingGenerator')
    def test_create_openai_generator(self, mock_openai):
        """Test creating OpenAI generator."""
        config = {
            'embedding_type': 'openai',
            'openai_api_key': 'test_key',
            'openai_model': 'text-embedding-ada-002'
        }
        
        generator = create_embedding_generator(config)
        
        mock_openai.assert_called_once_with(
            api_key='test_key',
            model='text-embedding-ada-002'
        )
    
    @unittest.skipIf(SKIP_HF_TESTS, "sentence-transformers not installed")
    @patch('es_to_pinecone_transfer.embeddings.HuggingFaceEmbeddingGenerator')
    def test_create_huggingface_generator(self, mock_hf):
        """Test creating HuggingFace generator."""
        config = {
            'embedding_type': 'huggingface',
            'huggingface_model': 'all-MiniLM-L6-v2'
        }
        
        generator = create_embedding_generator(config)
        
        mock_hf.assert_called_once_with('all-MiniLM-L6-v2')
    
    def test_create_random_generator(self):
        """Test creating random generator."""
        config = {'embedding_type': 'random'}
        
        generator = create_embedding_generator(config)
        
        self.assertIsInstance(generator, RandomEmbeddingGenerator)
    
    def test_missing_openai_key(self):
        """Test error when OpenAI key is missing."""
        config = {'embedding_type': 'openai'}
        
        with self.assertRaises(ConfigurationError):
            create_embedding_generator(config)
    
    def test_unsupported_type(self):
        """Test error with unsupported embedding type."""
        config = {'embedding_type': 'unsupported'}
        
        with self.assertRaises(ConfigurationError):
            create_embedding_generator(config)

if __name__ == '__main__':
    unittest.main()