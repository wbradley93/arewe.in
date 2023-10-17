from typing import Literal, Optional

class Team:
    def __init__(self, name: str, short_name: str, conference: str, team_name: Optional[str] = None, division: Optional[str] = None) -> None:
        self.name = name
        self.short_name = short_name
        self.team_name = team_name
        self.conference = conference
        self.division = division
        self.stats: dict[str, int] = {
            'wins': 0,
            'losses': 0
        }

    def update_stats(self, home_score: int, away_score: int) -> None:
        if home_score > away_score:
            self.stats['wins'] += 1
        else:
            self.stats['losses'] += 1

    def reset_stats(self) -> None:
        self.stats = {stat: 0 for stat in self.stats.keys()}

class NHLTeam(Team):
    def __init__(self, full_name: str, short_name: str, team_name: str, conference: Literal['Western', 'Eastern'],
                 division: Literal['Central', 'Pacific', 'Metropolitan', 'Atlantic']) -> None:
        super().__init__(name=full_name, short_name=short_name, conference=conference, team_name=team_name, division=division)
        self.stats |= {
            'regulation_wins': 0,
            'regulation_losses': 0,
            'overtime_wins': 0,
            'shootout_wins': 0,
            'overtime_losses': 0,
            'shootout_losses': 0,
            'overall_goals_for': 0,
            'overall_goals_against': 0
        }
    
    def get_overtime_shootout_loss_count(self) -> int:
        return self.stats['overtime_losses'] + self.stats['shootout_losses']
    
    def get_loss_count(self) -> int:
        return self.stats['regulation_losses'] + self.stats['overtime_losses'] + self.stats['shootout_losses']
    
    def get_regulation_overtime_win_count(self) -> int:
        return self.stats['regulation_wins'] + self.stats['overtime_wins']

    def get_win_count(self) -> int:
        return self.stats['regulation_wins'] + self.stats['overtime_wins'] + self.stats['shootout_wins']

    def get_regulation_win_count(self) -> int:
        return self.stats['regulation_wins']

    def get_points(self) -> int:
        return 2*self.get_win_count() + self.stats['overtime_losses'] + self.stats['shootout_losses']
    
    def get_overall_goals_for(self) -> int:
        return self.stats['overall_goals_for']
    
    def get_overall_goal_differential(self) -> int:
        return self.stats['overall_goals_for'] - self.stats['overall_goals_against']
    
    def get_games_played(self) -> int:
        return self.get_win_count() + self.get_loss_count()
    
    def get_points_percentage(self) -> float:
        return (self.get_points() / self.get_games_played()) / 2 if self.get_games_played() > 0 else 0
    
    def update_stats(self, goals_for:int, goals_against:int, result_type:Literal["R", "OT", "SO"]) -> None:
        if goals_for > goals_against:
            if result_type == "R":
                self.stats['regulation_wins'] += 1
            elif result_type == "OT":
                self.stats['overtime_wins'] += 1
            else:
                self.stats['shootout_wins'] += 1
        else:
            if result_type == "R":
                self.stats['regulation_losses'] += 1
            elif result_type == "OT":
                self.stats['overtime_losse'] += 1
            else:
                self.stats['shootout_losses'] += 1
        self.stats['overall_goals_for'] += goals_for
        self.stats['overall_goals_against'] += goals_against
    
    def standings_line(self) -> list[int | float | str]:
        diff = self.get_overall_goal_differential() if self.get_overall_goal_differential() < 1 else f"+{self.get_overall_goal_differential()}"
        # consistency here vs redundancy in extra getters?
        return [self.name, self.get_games_played(), self.get_win_count(), self.stats['regulation_losses'],
                self.get_overtime_shootout_loss_count(), self.get_points(), self.get_points_percentage(), self.stats['overall_goals_for'],
                self.stats['regulation_wins'], self.get_regulation_overtime_win_count(), self.stats['overall_goals_against'], diff]

    
class MLSTeam(Team):
    def __init__(self, name: str, short_name: str, conference: Literal['Western', 'Eastern']) -> None:
        super().__init__(name=name, short_name=short_name, conference=conference)
        self.stats |= {
            'ties': 0,
            'home_goals_for': 0,
            'home_goals_against': 0,
            'away_goals_for': 0,
            'away_goals_against': 0,
            'disciplinary_points': 0
        }
    
    def get_win_count(self) -> int:
        return self.stats['wins']
    
    def get_points(self) -> int:
        return 3*self.stats['wins'] + self.stats['ties']

    def get_home_goals_for(self) -> int:
        return self.stats['home_goals_for']

    def get_away_goals_for(self) -> int:
        return self.stats['away_goals_for']
    
    def get_home_goal_differential(self) -> int:
        return self.stats['home_goals_for'] - self.stats['home_goals_against']
    
    def get_away_goal_differential(self) -> int:
        return self.stats['away_goals_for'] - self.stats['away_goals_against']
    
    def get_goal_differential(self) -> int:
        return (self.stats['home_goals_for'] + self.stats['away_goals_for']) - (self.stats['home_goals_against'] + self.stats['away_goals_against'])
    
    def get_goals_for(self) -> int:
        return self.stats['home_goals_for'] + self.stats['away_goals_for']
    
    def get_goals_against(self) -> int:
        return self.stats['home_goals_against'] + self.stats['away_goals_against']
    
    def get_games_played(self) -> int:
        return self.stats['wins'] + self.stats['losses'] + self.stats['ties']
    
    def get_points_per_game(self) -> float:
        return round(self.get_points() / self.get_games_played(), 2) if self.get_games_played() > 0 else 0
    
    def get_disciplinary_points(self) -> int:
        return self.stats['disciplinary_points']

    def update_stats(self, goals_for:int, goals_against:int, home:bool, disciplinary_points:int) -> None:
        if home:
            self.stats['home_goals_for'] += goals_for
            self.stats['home_goals_against'] += goals_against
        else:
            self.stats['away_goals_for'] += goals_for
            self.stats['away_goals_against'] += goals_against
        
        if goals_for > goals_against:
            self.stats['wins'] += 1
        elif goals_for == goals_against:
            self.stats['ties'] += 1
        else:
            self.stats['losses'] += 1

        self.stats['disciplinary_points'] += disciplinary_points
    
    def standings_line(self) -> list[int | float | str]:
        diff = self.get_disciplinary_points() if self.get_disciplinary_points() < 1 else f"+{self.get_disciplinary_points()}"
        # consistency here vs redundancy in extra getters?
        return [self.name, self.get_points(), self.get_points_per_game(), self.get_games_played(),
                self.get_win_count(), self.stats['losses'], self.stats['ties'], self.get_goals_for(),
                self.get_goals_against(), diff]