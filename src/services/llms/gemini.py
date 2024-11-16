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
        return f"""Your task is reviewing pull requests. Instructions:
        - Provide the response in following JSON format: {{"reviews": [{{"lineNumber": <line_number>, "reviewComment": "<review comment>"}}]}}
        - Provide comments and suggestions ONLY if there is something to improve, otherwise "reviews" should be an empty array.
        - Use GitHub Markdown in comments
        - Focus on bugs, security issues, and performance problems
        - IMPORTANT: NEVER suggest adding comments to the code
        - Comment with language of human: {Config.HUMAN_LANGUAGE}

        Review the following code diff in the file "{file.path}" and take the pull request title and description into account.
        Pull request title: {pr_details.title}
        Pull request description:

        ---
        {pr_details.description or 'No description provided'}
        ---

        Git diff to review:

        ```diff
        {hunk.content}
        ```
        """

    def get_ai_response(self, prompt: str) -> List[Dict[str, str]]:
        """Get response from Gemini model."""
        try:
            response = self.model.generate_content(prompt)
            response_text = self._clean_response_text(response.text)
            return self._parse_response(response_text)
        except Exception as e:
            print(f"Error during Gemini API call: {e}")
            return []
