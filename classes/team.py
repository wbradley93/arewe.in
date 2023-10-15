from typing import Literal

class Team:
    def __init__(self, name: str) -> None:
        self.name = name
        self.wins = 0
        self.losses = 0
    
    def get_team_name(self) -> str:
        return self.name
    
    def get_win_count(self) -> int:
        return self.wins
    
    def get_loss_count(self) -> int:
        return self.losses
    
class NHLTeam(Team):
    def __init__(self, full_name: str, short_name: str, team_name: str, conference: Literal['Western', 'Eastern'], 
                 division: Literal['Central', 'Pacific', 'Metropolitan', 'Atlantic']) -> None:
        super().__init__(full_name)
        self.short_name = short_name
        self.team_name = team_name
        self.conference = conference
        self.division = division
        self.regulation_wins = 0
        self.regulation_losses = 0
        self.overtime_wins = 0
        self.shootout_wins = 0
        self.overtime_losses = 0
        self.shootout_losses = 0
        self.overall_goals_for = 0
        self.overall_goals_against = 0

    def get_short_name(self) -> str:
        return self.short_name

    def get_team_name(self) -> str:
        return self.team_name

    def get_conference(self) -> str:
        return self.conference

    def get_division(self) -> str:
        return self.division
    
    def get_regulation_loss_count(self) -> int:
        return self.regulation_losses
    
    def get_overtime_loss_count(self) -> int:
        return self.overtime_losses
    
    def get_shootout_loss_count(self) -> int:
        return self.shootout_losses
    
    def get_overtime_shootout_loss_count(self) -> int:
        return self.get_overtime_loss_count() + self.get_shootout_loss_count()
    
    def get_loss_count(self) -> int:
        return self.get_regulation_loss_count() + self.get_overtime_loss_count() + self.get_shootout_loss_count()
    
    def get_regulation_win_count(self) -> int:
        return self.regulation_wins
    
    def get_overtime_win_count(self) -> int:
        return self.overtime_wins
    
    def get_shootout_win_count(self) -> int:
        return self.shootout_wins
    
    def get_regulation_overtime_win_count(self) -> int:
        return self.get_regulation_win_count() + self.get_overtime_win_count()

    def get_win_count(self) -> int:
        return self.get_regulation_win_count() + self.get_overtime_win_count() + self.get_shootout_win_count()

    def get_points(self) -> int:
        return 2*self.get_win_count() + self.get_overtime_loss_count() + self.get_shootout_loss_count()
    
    def get_overall_goal_differential(self) -> int:
        return self.overall_goals_for - self.overall_goals_against
    
    def get_overall_goals_for(self) -> int:
        return self.overall_goals_for
    
    def get_overall_goals_against(self) -> int:
        return self.overall_goals_against
    
    def get_games_played(self) -> int:
        return self.get_win_count() + self.get_loss_count()
    
    def get_points_percentage(self) -> float:
        return (self.get_points() / self.get_games_played()) / 2 if self.get_games_played() > 0 else 0
    
    def reset_stats(self) -> None:
        self.regulation_wins = 0
        self.regulation_losses = 0
        self.overtime_wins = 0
        self.shootout_wins = 0
        self.overtime_losses = 0
        self.shootout_losses = 0
        self.overall_goals_for = 0
        self.overall_goals_against = 0
    
    def update_stats(self, victory:bool, result_type:Literal["R", "OT", "SO"], goals_for:int, goals_against:int) -> None:
        if victory:
            if result_type == "R":
                self.regulation_wins += 1
            elif result_type == "OT":
                self.overtime_wins += 1
            else:
                self.shootout_wins += 1
        else:
            if result_type == "R":
                self.regulation_losses += 1
            elif result_type == "OT":
                self.overtime_losses += 1
            else:
                self.shootout_losses += 1
        self.overall_goals_for += goals_for
        self.overall_goals_against += goals_against
    
    def standings_line(self) -> list[int | float | str]:
        diff = self.get_overall_goal_differential() if self.get_overall_goal_differential() < 1 else f"+{self.get_overall_goal_differential()}"
        return [self.get_team_name(), self.get_games_played(), self.get_win_count(), self.get_regulation_loss_count(), 
                self.get_overtime_shootout_loss_count(), self.get_points(), self.get_points_percentage(), self.get_overall_goals_for(),
                self.get_regulation_win_count(), self.get_regulation_overtime_win_count(), self.get_overall_goals_against(), diff]

    
class MLSTeam(Team):
    def __init__(self, name: str, short_name: str, conference: Literal['Western', 'Eastern']) -> None:
        super().__init__(name)
        self.short_name = short_name
        self.conference = conference
        self.ties = 0
        self.home_goals_for = 0
        self.home_goals_against = 0
        self.away_goals_for = 0
        self.away_goals_against = 0
        self.disciplinary_points = 0
    
    def get_tie_count(self) -> int:
        return self.ties
    
    def get_conference(self) -> str:
        return self.conference
    
    def get_points(self) -> int:
        return 3*self.wins + self.ties
    
    def get_home_goal_differential(self) -> int:
        return self.home_goals_for - self.home_goals_against
    
    def get_away_goal_differential(self) -> int:
        return self.away_goals_for - self.away_goals_against
    
    def get_goal_differential(self) -> int:
        return self.get_home_goal_differential() + self.get_away_goal_differential()
    
    def get_goals_for(self) -> int:
        return self.home_goals_for + self.away_goals_for
    
    def get_goals_against(self) -> int:
        return self.home_goals_against + self.away_goals_against
    
    def get_disciplinary_points(self) -> int:
        return self.disciplinary_points
    
    def get_away_goals_for(self) -> int:
        return self.away_goals_for
    
    def get_home_goals_for(self) -> int:
        return self.home_goals_for
    
    def get_games_played(self) -> int:
        return self.wins + self.losses + self.ties
    
    def get_points_per_game(self) -> float:
        return round(self.get_points() / self.get_games_played(), 2) if self.get_games_played() > 0 else 0
    
    def reset_stats(self) -> None:
        self.ties = 0
        self.home_goals_for = 0
        self.home_goals_against = 0
        self.away_goals_for = 0
        self.away_goals_against = 0
        self.disciplinary_points = 0
    
    def update_stats(self, home:bool, goals_for:int, goals_against:int, disciplinary_points:int) -> None:
        if home:
            self.home_goals_for += goals_for
            self.home_goals_against += goals_against
        else:
            self.away_goals_for += goals_for
            self.away_goals_against += goals_against
        
        if goals_for > goals_against: self.wins += 1
        elif goals_for == goals_against: self.ties += 1
        else: self.losses += 1

        self.disciplinary_points += disciplinary_points
    
    def standings_line(self) -> list[int | float | str]:
        diff = self.get_goal_differential() if self.get_goal_differential() < 1 else f"+{self.get_goal_differential()}"
        return [self.get_team_name(), self.get_points(), self.get_points_per_game(), self.get_games_played(), 
                self.get_win_count(), self.get_loss_count(), self.get_tie_count(), self.get_goals_for(),
                self.get_goals_against(), diff]