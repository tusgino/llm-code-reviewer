from typing import List, Dict, Any
from unidiff import PatchSet, PatchedFile, Hunk

class DiffParser:
  @staticmethod
  def parse_diff(diff_str: str) -> List[Dict[str, Any]]:
    """Parses the diff string and returns a structured format."""
    files = []
    current_file = None
    current_hunk = None

    for line in diff_str.splitlines(keepends=True):
        if line.startswith('index'):
            continue

        if line.startswith('diff --git'):
            if current_file:
                files.append(current_file)
            current_file = {'path': '', 'hunks': []}
            
        elif line.startswith('--- a/'):
            if current_file:
                current_file['path'] = line[6:]
                
        elif line.startswith('+++ b/'):
            if current_file:
                current_file['path'] = line[6:]
                
        elif line.startswith('@@'):
            if current_file:
                current_hunk = {'header': line, 'lines': []}
                current_file['hunks'].append(current_hunk)

        elif current_hunk is not None:
            current_hunk['lines'].append(line)
            
    if current_file:
        files.append(current_file)
        
    return files
