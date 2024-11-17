from typing import List, Dict
from anthropic import Anthropic
from unidiff import Hunk, PatchedFile
from ...core.config import Config
from ...core.models import PRDetails
from .base import BaseLLMService

class AnthropicService(BaseLLMService):
    """
    Implementation of BaseLLMService for Anthropic's Claude models.
    """
    
    def __init__(self):
        """Initialize the Anthropic client with configuration."""
        self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.model = Config.ANTHROPIC_MODEL
        
    def create_prompt(self, file: PatchedFile, hunk: Hunk, pr_details: PRDetails) -> str:
        """Create a prompt formatted for Anthropic's model expectations."""
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
        """Get response from Anthropic's Claude model."""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=0.2,
                system="You are an expert code reviewer.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            if response.content:
                # Extract the text content from the message
                response_text = response.content[0].text
                # Clean and parse the response
                cleaned_text = self._clean_response_text(response_text)
                return self._parse_response(cleaned_text)
            
            return []
            
        except Exception as e:
            print(f"Error during Anthropic API call: {e}")
            return []
