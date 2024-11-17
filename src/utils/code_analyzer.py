import re
from typing import List, Dict, Any
from unidiff import Hunk
from unidiff.patch import Line
from ..core.models import PRDetails, FileInfo
from ..services.ai_service import AIService
from ..libs.Hunk import NumberedHunk


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
  
  def _get_source_target_start(self, hunk_headers: str):
    match = re.match(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', hunk_headers)

    if match:
      source_start = int(match.group(1))
      target_start = int(match.group(3))
      source_length = int(match.group(2)) if match.group(2) else 1
      target_length = int(match.group(4)) if match.group(4) else 1
      return source_start, target_start, source_length, target_length

    return 1, 1, 1, 1

  def _process_file_hunks(
    self, file_info: FileInfo, file_data: Dict[str, Any], pr_details: PRDetails
  ) -> List[Dict[str, Any]]:
    """Processes hunks for a single file and generates comments."""
    comments = []
    
    for hunk_data in file_data.get("hunks", []):
      hunk_lines = hunk_data.get("lines", [])
      hunk_header = hunk_data.get("header", "")
      source_start, target_start, source_length, target_length = self._get_source_target_start(hunk_header)
      if not hunk_lines:
        continue
        
      hunk = self._create_hunk(hunk_lines, source_start, target_start, source_length, target_length)
      ai_response = self._get_ai_review(file_info, hunk, pr_details)
      if ai_response:
        comments.extend(self._create_comments(file_info, hunk, ai_response))
        
    return comments

  def _create_hunk(self, hunk_lines: List[str], source_start, target_start, source_length, target_length) -> Hunk:
    """Creates a Hunk object from a list of lines."""
    hunk = NumberedHunk(src_start=source_start, tgt_start=target_start, src_len=source_length, tgt_len=target_length)
    for line_str in hunk_lines:
        if line_str.startswith('+'):
            line = Line(value=line_str[1:], line_type='+')
        elif line_str.startswith('-'):
            line = Line(value=line_str[1:], line_type='-')
        else:
            line = Line(value=line_str, line_type=' ')
            
        hunk.append(line)
    
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
      side = response["side"].upper()
      if hunk.source_start <= line_number < hunk.source_start + hunk.source_length or hunk.target_start <= line_number < hunk.target_start + hunk.target_length:
        return {
          "body": response["reviewComment"],
          "path": file.path.strip(),
          "line": line_number,
          "side": side,
        }
    except (KeyError, TypeError, ValueError):
      pass
    return None
