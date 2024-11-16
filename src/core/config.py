import os
from github import Github

class Config:
    GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-1.5-flash-002')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')
    
    @classmethod
    def initialize_clients(cls):
        gh_client = Github(cls.GITHUB_TOKEN)
        return gh_client
