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
    comments = []

    for file_data in parsed_diff:
      file_path = file_data.get("path", "")
      if not file_path or file_path == "/dev/null":
        continue

      file_info = FileInfo(file_path)
      hunks = file_data.get("hunks", [])

      for hunk_data in hunks:
        hunk_lines = hunk_data.get("lines", [])
        if not hunk_lines:
          continue

        hunk = self._create_hunk(hunk_lines)
        prompt = self.ai_service.create_prompt(file_info, hunk, pr_details)
        ai_response = self.ai_service.get_ai_response(prompt)

        if ai_response:
          new_comments = self._create_comments(file_info, hunk, ai_response)
          comments.extend(new_comments)

    return comments

  def _create_hunk(self, hunk_lines: List[str]) -> Hunk:
    hunk = Hunk()
    hunk.source_start = 1
    hunk.source_length = len(hunk_lines)
    hunk.target_start = 1
    hunk.target_length = len(hunk_lines)
    hunk.content = "\n".join(hunk_lines)
    return hunk

  def _create_comments(
    self, file: FileInfo, hunk: Hunk, ai_responses: List[Dict[str, str]]
  ) -> List[Dict[str, Any]]:
    comments = []
    for ai_response in ai_responses:
      try:
        line_number = int(ai_response["lineNumber"])
        if 1 <= line_number <= hunk.source_length:
          comments.append(
            {
              "body": ai_response["reviewComment"],
              "path": file.path,
              "position": line_number,
            }
          )
      except (KeyError, TypeError, ValueError):
        continue
    return comments
