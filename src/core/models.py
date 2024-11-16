from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class PRDetails:
    owner: str
    repo: str
    pull_number: int
    title: str
    description: str

@dataclass
class FileInfo:
    path: str
