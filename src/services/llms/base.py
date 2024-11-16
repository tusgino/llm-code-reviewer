from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ...core.models import PRDetails


class BaseLLMService(ABC):
    @abstractmethod
    def create_prompt(self, file_path: str, diff_content: str, pr_details: PRDetails) -> str:
        pass
    
    @abstractmethod
    def get_review(self, prompt: str) -> List[Dict[str, Any]]:
        pass
