from typing import List, Dict, Any
from unidiff import Hunk
from ..core.models import PRDetails, FileInfo
from ..services.ai_service import AIService


class CodeAnalyzer:
  def __init__(self, ai_service: AIService):
    self.ai_service = ai_service

  def analyze_code(
    self, parsed_diff: List[Dict[str, Any]], pr_details: PRDetails
  ) -> List[Dict[str, Any]]:
    """
    Analyzes code changes and generates review comments.
    """
    comments = []
    
    for file_data in self._get_valid_files(parsed_diff):
      file_info = FileInfo(file_data["path"])
      comments.extend(self._process_file_hunks(file_info, file_data, pr_details))
      
    return comments

  def _get_valid_files(self, parsed_diff: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filters out invalid file paths from the diff."""
    return [
      file_data for file_data in parsed_diff
      if file_data.get("path") and file_data["path"] != "/dev/null"
    ]

  def _process_file_hunks(
    self, file_info: FileInfo, file_data: Dict[str, Any], pr_details: PRDetails
  ) -> List[Dict[str, Any]]:
    """Processes hunks for a single file and generates comments."""
    comments = []
    
    for hunk_data in file_data.get("hunks", []):
      hunk_lines = hunk_data.get("lines", [])
      if not hunk_lines:
        continue
        
      hunk = self._create_hunk(hunk_lines)
      ai_response = self._get_ai_review(file_info, hunk, pr_details)
      if ai_response:
        comments.extend(self._create_comments(file_info, hunk, ai_response))
        
    return comments

  def _create_hunk(self, hunk_lines: List[str]) -> Hunk:
    """Creates a Hunk object from a list of lines."""
    hunk = Hunk()
    length = len(hunk_lines)
    hunk.source_start = hunk.target_start = 1
    hunk.source_length = hunk.target_length = length
    hunk.content = "\n".join(hunk_lines)
    return hunk

  def _get_ai_review(
    self, file_info: FileInfo, hunk: Hunk, pr_details: PRDetails
  ) -> List[Dict[str, str]]:
    """Gets AI review comments for a code hunk."""
    prompt = self.ai_service.create_prompt(file_info, hunk, pr_details)
    return self.ai_service.get_ai_response(prompt)

  def _create_comments(
    self, file: FileInfo, hunk: Hunk, ai_responses: List[Dict[str, str]]
  ) -> List[Dict[str, Any]]:
    """Creates formatted comments from AI responses."""
    comments = []
    for response in ai_responses:
      comment = self._format_comment(file, hunk, response)
      if comment:
        comments.append(comment)
    return comments

  def _format_comment(
    self, file: FileInfo, hunk: Hunk, response: Dict[str, str]
  ) -> Dict[str, Any]:
    """Formats a single AI response into a comment."""
    try:
      line_number = int(response["lineNumber"])
      if 1 <= line_number <= hunk.source_length:
        return {
          "body": response["reviewComment"],
          "path": file.path,
          "position": line_number,
        }
    except (KeyError, TypeError, ValueError):
      pass
    return None
