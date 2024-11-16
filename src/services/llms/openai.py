from typing import List, Dict
from openai import OpenAI
from unidiff import Hunk, PatchedFile
from ...core.config import Config
from ...core.models import PRDetails
from .base import BaseLLMService

class OpenAIService(BaseLLMService):
    """
    Implementation of BaseLLMService for OpenAI's models.
    """
    
    def __init__(self):
        """Initialize the OpenAI client with configuration."""
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL
        
    def create_prompt(self, file: PatchedFile, hunk: Hunk, pr_details: PRDetails) -> str:
        """Create a prompt formatted for OpenAI's expectations."""
        return f"""Your task is reviewing pull requests. Instructions:
        - Provide the response in following JSON format: {{"reviews": [{{"lineNumber": <line_number>, "reviewComment": "<review comment>"}}]}}

        - Provide comments and suggestions ONLY if there is something to improve, otherwise "reviews" should be an empty array.
        - Use GitHub Markdown in comments
        - Focus on bugs, security issues, and performance problems
        - IMPORTANT: NEVER suggest adding comments to the code
        - IMPORTANT: Provide your review in {Config.HUMAN_LANGUAGE} language.

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
        """Get response from OpenAI model."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0.3,
                messages=[
                    {"role": "system", "content": "You are an expert code reviewer."},
                    {"role": "user", "content": prompt}
                ]
            )
            if response.choices:
                response_text = self._clean_response_text(response.choices[0].message.content)
                return self._parse_response(response_text)
            return []
        except Exception as e:
            print(f"Error during OpenAI API call: {e}")
            return []
