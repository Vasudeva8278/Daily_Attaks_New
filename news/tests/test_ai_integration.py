from django.test import TestCase
from django.conf import settings
from unittest.mock import patch, MagicMock
from ..ai_integration import GeminiIntegration

class TestGeminiIntegration(TestCase):
    def setUp(self):
        settings.GEMINI_API_KEY = 'test-api-key'
        self.gemini = GeminiIntegration()
        
    @patch('google.generativeai.GenerativeModel')
    def test_enhance_content(self, mock_model):
        # Mock the Gemini API response
        mock_response = MagicMock()
        mock_response.text = "Enhanced content"
        mock_model.return_value.generate_content.return_value = mock_response
        
        # Test content enhancement
        content = "Original content"
        parameters = {
            'tone': 'professional',
            'length': 'medium',
            'target_audience': 'general',
            'style': 'news'
        }
        
        result = self.gemini.enhance_content(content, parameters)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['content'], "Enhanced content")
        self.assertEqual(result['parameters'], parameters)
        self.assertEqual(result['original_length'], len(content))
        self.assertEqual(result['enhanced_length'], len("Enhanced content"))
        
    @patch('google.generativeai.GenerativeModel')
    def test_enhance_content_error(self, mock_model):
        # Mock API error
        mock_model.return_value.generate_content.side_effect = Exception("API Error")
        
        result = self.gemini.enhance_content("Test content")
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        
    @patch('google.generativeai.GenerativeModel')
    def test_generate_headline(self, mock_model):
        # Mock the Gemini API response
        mock_response = MagicMock()
        mock_response.text = "Test Headline"
        mock_model.return_value.generate_content.return_value = mock_response
        
        # Test headline generation
        content = "Article content"
        style = "news"
        
        result = self.gemini.generate_headline(content, style)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['headline'], "Test Headline")
        self.assertEqual(result['style'], style)
        
    @patch('google.generativeai.GenerativeModel')
    def test_generate_headline_error(self, mock_model):
        # Mock API error
        mock_model.return_value.generate_content.side_effect = Exception("API Error")
        
        result = self.gemini.generate_headline("Test content")
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        
    def test_missing_api_key(self):
        # Temporarily remove API key
        original_key = settings.GEMINI_API_KEY
        settings.GEMINI_API_KEY = None
        
        with self.assertRaises(ValueError):
            GeminiIntegration()
            
        # Restore API key
        settings.GEMINI_API_KEY = original_key 