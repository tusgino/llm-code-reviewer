import json
from typing import List, Dict, Any, Optional
import google.generativeai as Client
from unidiff import Hunk, PatchedFile
from ..core.config import Config
from ..core.models import PRDetails, FileInfo


class AIService:
  def __init__(self):
    self.model = Client.GenerativeModel(Config.GEMINI_MODEL)

  def create_prompt(
    self, file: PatchedFile, hunk: Hunk, pr_details: PRDetails
  ) -> str:
    return f"""Your task is reviewing pull requests. Instructions:
    - Provide the response in following JSON format: {{"reviews": [{{"lineNumber": <line_number>, "reviewComment": "<review comment>"}}]}}
    - Provide comments and suggestions ONLY if there is something to improve, otherwise "reviews" should be an empty array.
    - Use GitHub Markdown in comments
    - Focus on bugs, security issues, and performance problems
    - IMPORTANT: NEVER suggest adding comments to the code

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
    try:
      response = self.model.generate_content(prompt)
      response_text = self._clean_response_text(response.text)
      return self._parse_response(response_text)
    except Exception as e:
      print(f"Error during Gemini API call: {e}")
      return []

  def _clean_response_text(self, text: str) -> str:
    text = text.strip()
    if text.startswith('```json'):
      text = text[7:]
    if text.endswith('```'):
      text = text[:-3]
    return text.strip()

  def _parse_response(self, response_text: str) -> List[Dict[str, str]]:
    try:
      data = json.loads(response_text)
      if "reviews" in data and isinstance(data["reviews"], list):
        return [
          review
          for review in data["reviews"]
          if "lineNumber" in review and "reviewComment" in review
        ]
      return []
    except json.JSONDecodeError:
      return []
