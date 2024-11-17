from typing import List, Dict
import google.generativeai as Client
from unidiff import Hunk, PatchedFile
from ...core.config import Config
from ...core.models import PRDetails
from .base import BaseLLMService

class GeminiService(BaseLLMService):
    """
    Implementation of BaseLLMService for Google's Gemini model.
    """
    
    def __init__(self):
        """Initialize the Gemini service with configuration."""
        Client.configure(api_key=Config.GEMINI_API_KEY)
        self.model = Client.GenerativeModel(Config.GEMINI_MODEL)
        
    def create_prompt(self, file: PatchedFile, hunk: Hunk, pr_details: PRDetails) -> str:
        """Create a prompt formatted for Gemini's expectations."""
        return f"""
            Your task is to review the following code changes. Please follow these guidelines:
            Provide your response in this JSON format:
            {{"reviews": [{{"lineNumber": <line_number>, "reviewComment": "<review comment>, side: "<left or right >, "filepath": "<file path>"}}]}}
            Important Rules:
            1. Line Number Validation:
            - For "left" side: {hunk.source_start} ≤ lineNumber < {hunk.source_start + hunk.source_length}
            - For "right" side: {hunk.target_start} ≤ lineNumber < {hunk.target_start + hunk.target_length}

            2. Review Focus Areas:
            - Critical bugs and errors
            - Security vulnerabilities and risks
            - Performance optimization opportunities 
            - Code architecture and maintainability issues
            - Suggest code for improvement and optimization

            3. Key Requirements:
            - Return empty "reviews" array if no issues found
            - Use GitHub Markdown formatting in your comments
            - Do NOT suggest adding code comments
            - Provide feedback in language: {Config.HUMAN_LANGUAGE}

            Context Information:
            File: {file.path}
            PR Title: {pr_details.title}
            PR Description: 
            ---
            {pr_details.description or 'No description provided'}
            ---

            Git Diff Details:
            - Source Start: {hunk.source_start}
            - Source Length: {hunk.source_length} 
            - Target Start: {hunk.target_start}
            - Target Length: {hunk.target_length}

            Code Diff to Review:
            ```diff
            {hunk.__str__()}
            ```
        """

    def get_ai_response(self, prompt: str) -> List[Dict[str, str]]:
        """Get response from Gemini model."""
        try:
            response = self.model.generate_content(prompt, generation_config={'max_output_tokens': 1024, 'temperature': 0.3})
            response_text = self._clean_response_text(response.text)
            return self._parse_response(response_text)
        except Exception as e:
            print(f"Error during Gemini API call: {e}")
            return []
