from dataclasses import dataclass
from typing import List

@dataclass
class Exercise:
    exercise_id: str
    node: str
    difficulty: int
    type: str
    estimated_time: float
    prerequisites: List[str]
