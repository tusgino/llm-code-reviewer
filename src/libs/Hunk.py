from unidiff import Hunk
from typing import List

class NumberedHunk(Hunk):
    def __str__(self) -> str:
        """Override string representation to include line numbers."""
        source_line = self.source_start
        target_line = self.target_start
        result = []
        
        # Add the standard hunk header
        # result.append(f"@@ -{self.source_start},{self.source_length} +{self.target_start},{self.target_length} @@")
        
        # Add numbered lines
        for line in self:
            if line.is_removed:
                result.append(f"{source_line:4d} {' ':4} -{line.value.rstrip()}")
                source_line += 1
            elif line.is_added:
                result.append(f"{' ':4} {target_line:4d} +{line.value.rstrip()}")
                target_line += 1
            else:  # context line
                result.append(f"{source_line:4d} {target_line:4d} {line.value.rstrip()}")
                source_line += 1
                target_line += 1
                
        return '\n'.join(result)
