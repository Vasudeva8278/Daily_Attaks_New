import os
import google.generativeai as genai
from django.conf import settings
from typing import Dict, Any, Optional

class GeminiIntegration:
    def __init__(self):
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set in settings")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
    def enhance_content(self, content: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Enhance content using Gemini API with configurable parameters.
        
        Args:
            content (str): The content to enhance
            parameters (dict, optional): Enhancement parameters including:
                - tone: str (e.g., 'professional', 'casual', 'formal')
                - length: str (e.g., 'short', 'medium', 'long')
                - target_audience: str (e.g., 'general', 'technical', 'business')
                - style: str (e.g., 'news', 'blog', 'report')
        
        Returns:
            dict: Enhanced content and metadata
        """
        if not parameters:
            parameters = {}
            
        prompt = self._build_prompt(content, parameters)
        
        try:
            response = self.model.generate_content(prompt)
            enhanced_content = response.text
            
            return {
                'content': enhanced_content,
                'parameters': parameters,
                'original_length': len(content),
                'enhanced_length': len(enhanced_content),
                'success': True
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    def generate_headline(self, content: str, style: str = 'news') -> Dict[str, Any]:
        """
        Generate a headline for the content using Gemini API.
        
        Args:
            content (str): The content to generate a headline for
            style (str): The style of headline to generate
        
        Returns:
            dict: Generated headline and metadata
        """
        prompt = f"""
        Generate a {style} headline for the following content.
        The headline should be engaging, accurate, and optimized for SEO.
        
        Content:
        {content}
        """
        
        try:
            response = self.model.generate_content(prompt)
            headline = response.text.strip()
            
            return {
                'headline': headline,
                'style': style,
                'success': True
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    def _build_prompt(self, content: str, parameters: Dict[str, Any]) -> str:
        """
        Build a prompt for the Gemini API based on content and parameters.
        """
        tone = parameters.get('tone', 'professional')
        length = parameters.get('length', 'medium')
        target_audience = parameters.get('target_audience', 'general')
        style = parameters.get('style', 'news')
        
        prompt = f"""
        Enhance the following content with the following parameters:
        - Tone: {tone}
        - Length: {length}
        - Target Audience: {target_audience}
        - Style: {style}
        
        The enhanced content should:
        1. Maintain the original meaning and key points
        2. Improve clarity and readability
        3. Optimize for the specified tone and audience
        4. Follow the requested length guidelines
        5. Maintain proper grammar and style
        
        Original Content:
        {content}
        
        Please provide the enhanced version of this content.
        """
        
        return prompt 