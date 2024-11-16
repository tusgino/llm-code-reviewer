import os
import json
from typing import List, Dict, Any
import fnmatch
from .core.config import Config
from .core.models import PRDetails
from .services.github_service import GitHubService
from .services.ai_service import AIService
from .utils.diff_parser import DiffParser
from .utils.code_analyzer import CodeAnalyzer

class PRReviewApplication:
  def __init__(self):
    gh_client = Config.initialize_clients()
    self.github_service = GitHubService(gh_client)
    self.ai_service = AIService()
    self.code_analyzer = CodeAnalyzer(self.ai_service)
    self.diff_parser = DiffParser()

  def run(self):
    try:
      event_name = os.environ.get("GITHUB_EVENT_NAME")
      if event_name != "issue_comment":
        print("Unsupported event:", event_name)
        return

      pr_details = self.github_service.get_pr_details(os.environ["GITHUB_EVENT_PATH"])
      diff = self.github_service.get_diff(pr_details.owner, pr_details.repo, pr_details.pull_number)
      if not diff:
        print("No diff found")
        return

      parsed_diff = self.diff_parser.parse_diff(diff)
      filtered_diff = self._filter_diff(parsed_diff)
      comments = self.code_analyzer.analyze_code(filtered_diff, pr_details)
      if comments:
        self.github_service.create_review_comment(pr_details, comments)

    except Exception as error:
      print("Error:", error)

  def _filter_diff(self, parsed_diff: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    exclude_patterns = os.environ.get("INPUT_EXCLUDE", "").split(",")
    exclude_patterns = [s.strip() for s in exclude_patterns]

    return [
      file for file in parsed_diff
      if not any(fnmatch.fnmatch(file.get('path', ''), pattern)
        for pattern in exclude_patterns)
    ]

if __name__ == "__main__":
  app = PRReviewApplication()
  app.run()
