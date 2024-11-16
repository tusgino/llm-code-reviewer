from typing import List, Dict
from unidiff import Hunk, PatchedFile

from ..core.config import Config
from ..core.models import PRDetails
from .llms.gemini import GeminiService
from .llms.openai import OpenAIService
from .llms.anthropic import AnthropicService

class AIService:
    """
    Service manager that handles selection and usage of available LLM services.
    Prioritizes Gemini if both services are available.
    """
    
    def __init__(self):
        """Initialize available LLM services based on configuration."""
        self.active_service = None
        self._initialize_service()

    def _initialize_service(self) -> None:
        """Initialize the appropriate LLM service based on available API keys."""
        PRIMARY_MODEL = getattr(Config, 'PRIMARY_MODEL', 'gemini').lower()
        SUPPORTED_MODELS = {
            'gemini': GeminiService,
            'openai': OpenAIService,
            'anthropic': AnthropicService
        }

        if PRIMARY_MODEL not in SUPPORTED_MODELS:
            print(f"Unsupported PRIMARY_MODEL '{PRIMARY_MODEL}'. Using default order.")
            ordered_models = list(SUPPORTED_MODELS.keys())
        else:
            ordered_models = [PRIMARY_MODEL] + [
                model for model in SUPPORTED_MODELS if model != PRIMARY_MODEL
            ]

        for model in ordered_models:
            if self.check_key_model_availability(model):
                try:
                    self.active_service = SUPPORTED_MODELS[model]()
                    print(f"Initialized {model.title()} service")
                    break
                except Exception as e:
                    print(f"Failed to initialize {model.title()} service: {e}")

        if not self.active_service:
            raise ValueError("No LLM service could be initialized. Please check your API keys.")

    def check_key_model_availability(self, model: str) -> bool:
        """Check if the API key for specified model is available.

        Args:
            model: Service name ('openai', 'gemini', or 'anthropic')

        Returns:
            bool: True if API key is available
        """
        key_name = f"{model.upper()}_API_KEY"
        return hasattr(Config, key_name) and getattr(Config, key_name)

    def create_prompt(self, file: PatchedFile, hunk: Hunk, pr_details: PRDetails) -> str:
        """
        Create a prompt using the active LLM service.
        
        Args:
            file: The file being reviewed
            hunk: The code hunk to review
            pr_details: Pull request details
            
        Returns:
            str: Formatted prompt for the active LLM service
        """
        if not self.active_service:
            raise RuntimeError("No active LLM service available")
        return self.active_service.create_prompt(file, hunk, pr_details)

    def get_ai_response(self, prompt: str) -> List[Dict[str, str]]:
        """
        Get response from the active LLM service.
        
        Args:
            prompt: The formatted prompt to send to the LLM
            
        Returns:
            List[Dict[str, str]]: List of review comments
        """
        if not self.active_service:
            raise RuntimeError("No active LLM service available")
            
        try:
            return self.active_service.get_ai_response(prompt)
        except Exception as e:
            print(f"Error getting AI response: {e}")
            return []

    def get_active_service_name(self) -> str:
        """
        Get the name of the currently active service.
        
        Returns:
            str: Name of the active service or 'None' if no service is active
        """
        if not self.active_service:
            return "None"
        return self.active_service.__class__.__name__
