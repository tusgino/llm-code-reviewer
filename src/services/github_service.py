import json
import requests
from typing import List, Dict, Any
from ..core.config import Config
from ..core.models import PRDetails
from github import Github
from github.Repository import Repository

class GitHubService:
  def __init__(self, gh_client):
    self.gh_client = gh_client

  def get_pr_details(self, event_path: str) -> PRDetails:
    with open(event_path, "r") as f:
      event_data = json.load(f)

    if "issue" in event_data and "pull_request" in event_data["issue"]:
      pull_number = event_data["issue"]["number"]
    else:
      pull_number = event_data["number"]

    repo_full_name = event_data["repository"]["full_name"]
    owner, repo = repo_full_name.split("/")

    repo_obj = self.gh_client.get_repo(repo_full_name)
    pr = repo_obj.get_pull(pull_number)

    return PRDetails(owner, repo_obj.name, pull_number, pr.title, pr.body)

  def get_diff(self, owner: str, repo: str, pull_number: int) -> str:
    repo_name = f"{owner}/{repo}"
    api_url = f"https://api.github.com/repos/{repo_name}/pulls/{pull_number}"

    headers = {
      'Authorization': f'Bearer {Config.GITHUB_TOKEN}',
      'Accept': 'application/vnd.github.v3.diff'
    }

    response = requests.get(f"{api_url}.diff", headers=headers)
    if response.status_code == 200:
      return response.text
    return ""

  def create_review_comment(self, pr_details: PRDetails, comments: List[Dict[str, Any]]):
    repo = self.gh_client.get_repo(f"{pr_details.owner}/{pr_details.repo}")
    pr = repo.get_pull(pr_details.pull_number)
    
    pr.create_review(
      body="Gemini AI Code Reviewer Comments",
      comments=comments,
      event="COMMENT"
    )
