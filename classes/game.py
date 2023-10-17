from datetime import datetime
from typing import Literal

class Game:
    def __init__(self, home_id: int, away_id: int, start_datetime: datetime, status: str,
                 home_score: int = 0, away_score: int = 0) -> None:
        self.home_id = home_id
        self.away_id = away_id
        self.status = status
        self.start = start_datetime
        self.home_score = home_score
        self.away_score = away_score

    def update(self, status: str, home_score: int, away_score: int) -> None:
        self.status = status
        self.home_score = home_score
        self.away_score = away_score
    
class MLSGame(Game):
    def __init__(self, home_id: int, away_id: int, start_datetime: datetime, status: str, home_score: int = 0,
                 away_score: int = 0, home_disciplinary_points: int = 0, away_disciplinary_points: int = 0) -> None:
        super().__init__(home_id, away_id, start_datetime, status, home_score, away_score)
        self.home_disciplinary_points = home_disciplinary_points
        self.away_disciplinary_points = away_disciplinary_points
            
class NHLGame(Game):
    def __init__(self, home_id: int, away_id: int, start_datetime: datetime, status: str, home_score: int = 0,
                 away_score: int = 0, result_type: Literal["R", "OT", "SO"] = None) -> None:
        super().__init__(home_id, away_id, start_datetime, status, home_score, away_score)
        self.result_type = result_type