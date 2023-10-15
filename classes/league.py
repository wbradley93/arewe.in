from classes.team import Team, MLSTeam, NHLTeam
from classes.game import Game, MLSGame, NHLGame
from typing import Literal, Optional
from typing_extensions import override
from datetime import datetime

mls_standings_header: list[str] = ["Club", "Points", "Points Per Game", "Games Played", "Wins", "Losses", "Ties", "Goals For", 
                                   "Goals Against", "Goal Differential"]
mls_standings_header_compact: list[str] = ["Club", "Points", "PPG", "GP", "W", "L", "T", "GF", "GA", "GD"]
def mls_standings_rules(t: MLSTeam) -> tuple[int, ...]:
    return (                                        # 2023 MLS Standings/Tiebreaker Rules
            t.get_points(),                         # 1.  Total number of points
            t.get_win_count(),                      # 2.  Total number of wins
            t.get_goal_differential(),              # 3.  Overall goal differential
            t.get_goals_for(),                      # 4.  Total number of goals scored
            -t.get_disciplinary_points(),           # 5.  Fewest Disciplinary Points
            t.get_away_goal_differential(),         # 6.  Away goal differential
            t.get_away_goals_for(),                 # 7.  Total number of away goals scored
            t.get_home_goal_differential(),         # 8.  Home goal differential
            t.get_home_goals_for()                  # 9.  Total number of home goals scored
    )                                               # 10. Coin flip

nhl_standings_header: list[str] = ["Team", "Games Played", "Wins", "Regulation Losses", "Overtime/Shootout Losses", 
                                   "Points", "Points %", "Goals For", "Regulation Wins", "Regulation/Overtime Wins", 
                                   "Goals Against", "Goal Differential"]
nhl_standings_header_compact: list[str] = ["Team", "GP", "W", "L", "OTL/SOL", "Points", "Points %", "GF", "RW", "ROW", "GA", "DIFF"]
def nhl_standings_rules(t: NHLTeam) -> tuple[int, ...]:
    return (                                            # 2023-24 NHL Standings/Tiebreaker Rules
        t.get_points(),                                 # 1. Total number of points
        -t.get_games_played(),                          # 2. Points percentage (if 1 is tied, that means fewest games played wins)
        t.get_regulation_win_count(),                   # 3. Regulation wins
        t.get_regulation_overtime_win_count(),          # 4. Regulation wins + OT wins
        t.get_win_count(),                              # 5. Overall wins
        # t.                                              # 6. Points earned in games among tied teams
        t.get_overall_goal_differential(),              # 7. Goal differential (including goals counted for shootout wins/losses)
        t.get_overall_goals_for()                       # 8. Total number of goals scored (including goals awarded for shootout wins)
    )

class League:
    def __init__(self, standings_header: list[str], standings_header_compact: list[str], standings_rules: tuple[int, ...]) -> None:
        self.teams: dict[int, Team] = {}
        self.games: list[Game] = []
        self.standings_header = standings_header
        self.standings_header_compact = standings_header_compact
        self.standings_rules = standings_rules

    def add_team(self, name: str) -> None:
        self.teams[len(self.teams)] = Team(name)

    # def add_game(self, home_id: int, away_id: int, start_datetime: datetime) -> None:
    #     self.games.append(Game(home_id, away_id, start_datetime))

    def get_standings_header(self, compact:bool):
        return self.standings_header_compact if compact else self.standings_header

    def standings(self):
        return sorted(self.teams.values(), key=self.standings_rules, reverse=True)

class MLSLeague(League):
    @override
    def __init__(self) -> None:
        super().__init__(mls_standings_header, mls_standings_header_compact, mls_standings_rules)
        self.teams: dict[int, MLSTeam] = {}
        self.games: dict[int, MLSGame] = {}

    @override
    def add_team(self, name: str, short_name: str, conference: Literal["Western", "Eastern"], id: int = None) -> None:
        if id is None: id = len(self.teams)
        self.teams[id] = MLSTeam(name, short_name, conference)

    def add_game(self, game_id: int, home_id: int, away_id: int, start_datetime: datetime, status: str, home_score: int = 0, 
                 away_score: int = 0, home_disciplinary_points: int = 0, away_disciplinary_points: int = 0) -> None:
        self.games[game_id] = MLSGame(game_id, home_id, away_id, start_datetime, status, home_score, away_score, 
                                      home_disciplinary_points, away_disciplinary_points)

    @override
    def standings(self, conference: Literal["Western", "Eastern"]):
        return sorted(filter(lambda t: t.get_conference() == conference, self.teams.values()), key=self.standings_rules, reverse=True)
    
    def update_official_stats(self):
        for team in self.teams.values():
            team.reset_stats()

        for game in self.games.values():
            if game.status == "FullTime":
                self.teams[game.home_id].update_stats(True, game.home_score, game.away_score, 0)
                self.teams[game.away_id].update_stats(False, game.away_score, game.home_score, 0)
    

class NHLLeague(League):
    @override
    def __init__(self) -> None:
        super().__init__(nhl_standings_header, nhl_standings_header_compact, nhl_standings_rules)
        self.teams: dict[int, NHLTeam] = {}
        self.games: dict[int, NHLGame] = {}

    @override
    def add_team(self, name: str, short_name: str, team_name: str, conference: Literal["Western", "Eastern"],
                 division: Literal['Central', 'Pacific', 'Metropolitan', 'Atlantic'], id: int = None) -> None:
        if id is None: id = len(self.teams)
        self.teams[id] = NHLTeam(name, short_name, team_name, conference, division)

    def add_game(self, game_id: int, home_id: int, away_id: int, start_datetime: datetime, status: str, home_score: int = 0, 
                 away_score: int = 0, result_type: Literal["R", "OT", "SO"] = None) -> None:
        self.games[game_id] = NHLGame(game_id, home_id, away_id, start_datetime, status, home_score, away_score, result_type)

    @override
    def standings(self, standings_type: Literal["conference", "division"], conference: Optional[Literal["Western", "Eastern"]], 
                             division: Optional[Literal['Central', 'Pacific', 'Metropolitan', 'Atlantic']]):
        if standings_type == "conference" and conference is not None:
            rows = sorted(filter(lambda t: t.get_conference() == conference, self.teams.values()), key=self.standings_rules, reverse=True)
        elif standings_type == "division" and division is not None:
            rows = sorted(filter(lambda t: t.get_division() == division, self.teams.values()), key=self.standings_rules, reverse=True)
        else:
            raise ValueError()
        return rows
    
    def update_official_stats(self):
        for team in self.teams.values():
            team.reset_stats()

        for game in self.games.values():
            if game.status == "Final":
                self.teams[game.home_id].update_stats(game.home_score > game.away_score, game.result_type, game.home_score, game.away_score)
                self.teams[game.away_id].update_stats(game.home_score < game.away_score, game.result_type, game.away_score, game.home_score)