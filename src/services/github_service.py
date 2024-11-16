import json
import requests
from typing import List, Dict, Any
from ..core.config import Config
from ..core.models import PRDetails
from github import Github
from github.Repository import Repository

class GitHubService:
  def __init__(self, gh_client: Github):
    """Initialize GitHub service with a client."""
    self.gh_client = gh_client

  def get_pr_details(self, event_path: str) -> PRDetails:
    """
    Extract pull request details from GitHub event data.
    
    Args:
      event_path: Path to GitHub event JSON file
    Returns:
      PRDetails object containing PR information
    """
    event_data = self._load_event_data(event_path)
    pull_number = self._extract_pull_number(event_data)
    repo_full_name = event_data["repository"]["full_name"]
    owner, repo = repo_full_name.split("/")
    
    repo_obj = self.gh_client.get_repo(repo_full_name)
    pr = repo_obj.get_pull(pull_number)

    return PRDetails(owner, repo_obj.name, pull_number, pr.title, pr.body)

  def get_diff(self, owner: str, repo: str, pull_number: int) -> str:
    """
    Get the diff content for a pull request.
    
    Returns:
      Diff content as string or empty string if request fails
    """
    api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}.diff"
    headers = {
      'Authorization': f'Bearer {Config.GITHUB_TOKEN}',
      'Accept': 'application/vnd.github.v3.diff'
    }

    response = requests.get(api_url, headers=headers)
    return response.text if response.status_code == 200 else ""

  def create_review_comment(self, pr_details: PRDetails, comments: List[Dict[str, Any]]) -> None:
    """Create a review comment on the pull request."""
    repo = self.gh_client.get_repo(f"{pr_details.owner}/{pr_details.repo}")
    pr = repo.get_pull(pr_details.pull_number)
    
    pr.create_review(
      body="AI generated review comments",
      comments=comments,
      event="COMMENT"
    )

  def _load_event_data(self, event_path: str) -> Dict:
    """Load GitHub event data from JSON file."""
    with open(event_path, "r") as f:
      return json.load(f)

  def _extract_pull_number(self, event_data: Dict) -> int:
    """Extract pull request number from event data."""
    if "issue" in event_data and "pull_request" in event_data["issue"]:
      return event_data["issue"]["number"]
    return event_data["number"]
