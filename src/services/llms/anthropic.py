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
        
        - Provide your response in this JSON format:
          {{"reviews": [{{"lineNumber": <line_number>, "reviewComment": "<review comment>"}}]}}
        
        - Only provide comments for code that needs improvement
        - If no improvements are needed, return an empty "reviews" array
        - Use GitHub Markdown formatting in your comments
        - Focus on:
          * Potential bugs
          * Security vulnerabilities
          * Performance issues
          * Code structure and maintainability
        - IMPORTANT: Provide your review in {Config.HUMAN_LANGUAGE} language
        
        File being reviewed: "{file.path}"
        
        Pull request title: {pr_details.title}
        
        Pull request description:
        ---
        {pr_details.description or 'No description provided'}
        ---

        Code changes to review:
        ```diff
        {hunk.content}
        ```
        """

    def get_ai_response(self, prompt: str) -> List[Dict[str, str]]:
        """Get response from Anthropic's Claude model."""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=0.7,
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
