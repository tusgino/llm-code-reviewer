import os
import google.generativeai as Client
from github import Github
from typing import Tuple

class Config:
    GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-1.5-flash-002')
    
    @classmethod
    def initialize_clients(cls):
        gh_client = Github(cls.GITHUB_TOKEN)
        Client.configure(api_key=cls.GEMINI_API_KEY)
        return gh_client
