from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class UserState:
    knowledge: Dict[str, float]           # e.g. {"notes": 0.7, ...}
    accuracy: Dict[str, float]            # e.g. {"notes": 0.8, ...}
    attempts: Dict[str, int]              # e.g. {"notes": 12, ...}
    streak: int                           # consecutive correct/incorrect
    last_exercise_difficulty: int         # 1-10
    time_since_last_practice: float       # in hours
    recent_performance_trend: Dict[str, List[float]]  # e.g. {"notes": [1,0,1,1], ...}
