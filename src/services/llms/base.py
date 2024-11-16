# src/services/llm/base.py
from abc import ABC, abstractmethod
import json
from typing import List, Dict
from unidiff import Hunk, PatchedFile
from ...core.models import PRDetails

class BaseLLMService(ABC):
    """
    Abstract base class for LLM services defining the common interface
    that all LLM implementations must follow.
    """
    
    @abstractmethod
    def create_prompt(self, file: PatchedFile, hunk: Hunk, pr_details: PRDetails) -> str:
        """
        Create a prompt for the LLM model.
        
        Args:
            file: The file being reviewed
            hunk: The code hunk to review
            pr_details: Pull request details
            
        Returns:
            str: Formatted prompt for the LLM
        """
        pass

    @abstractmethod
    def get_ai_response(self, prompt: str) -> List[Dict[str, str]]:
        """
        Get response from the LLM model.
        
        Args:
            prompt: The formatted prompt to send to the LLM
            
        Returns:
            List[Dict[str, str]]: List of review comments
        """
        pass

    def _clean_response_text(self, text: str) -> str:
        """
        Clean the raw response text from the LLM.
        
        Args:
            text: Raw response text
            
        Returns:
            str: Cleaned text
        """
        text = text.strip()
        if text.startswith('```json'):
            text = text[7:]
        if text.endswith('```'):
            text = text[:-3]
        return text.strip()

    def _parse_response(self, response_text: str) -> List[Dict[str, str]]:
        """
        Parse the cleaned response text into structured data.
        
        Args:
            response_text: Cleaned response text
            
        Returns:
            List[Dict[str, str]]: Parsed review comments
        """
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
