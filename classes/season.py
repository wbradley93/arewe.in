from classes.team import Team, MLSTeam, NHLTeam
from classes.game import Game, MLSGame, NHLGame
from utils.serializer import serializer
from typing import Literal, Optional
from typing_extensions import override
from copy import deepcopy
from datetime import datetime
import json
import requests

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

class Season:
    def __init__(self, standings_header: list[str], standings_header_compact: list[str], standings_rules: tuple[int, ...]) -> None:
        self.teams: dict[int, Team] = {}
        self.games: dict[int, Game] = {}
        self.standings_header = standings_header
        self.standings_header_compact = standings_header_compact
        self.standings_rules = standings_rules

    def add_team(self, name: str) -> None:
        self.teams[len(self.teams)] = Team(name)

    def get_standings_header(self, compact:bool):
        return self.standings_header_compact if compact else self.standings_header

    # TODO
    # remove stats from Team - should be running calcs over Games, maybe persisting them in Season?
    # - once a game is Final, it won't be changing - makes sense to persist official standings, validate them occasionally?
    # - then use this same code, but filter the official standings (will need to add conference/division to those objects)
    # - then use simulate_games with deepcopy as shown
    def standings(self, conference: str = None, division: str = None, live: bool = False):
        teams = self.teams.values() if not live else self.simulate_games(filter(lambda g: g.status == "Live", self.games.values()))

        if division is not None:
            standings_teams = filter(lambda t: t.get_division() == division, teams)
        elif conference is not None:
            standings_teams = filter(lambda t: t.get_conference() == conference, teams)
        else:
            standings_teams = teams
        
        return [t.standings_line() for t in sorted(standings_teams, key=self.standings_rules, reverse=True)]

    # use this for projections and also for live standings
    # TODO override in subclasses
    def simulate_games(self, games: list[Game]) -> None:
        simulated_teams = deepcopy(self.teams)
        for game in games:
            simulated_teams[game.home_id].update_stats(game.home_score, game.away_score)
            simulated_teams[game.away_id].update_stats(game.away_score, game.home_score)
        return simulated_teams

    def validate_standings(self) -> None:
        # TODO
        pass

    def json(self):
        return json.dumps({"teams": self.teams, "games": self.games}, default=serializer, sort_keys=True)

class MLSSeason(Season):
    @override
    def __init__(self, start_year: int) -> None:
        super().__init__(mls_standings_header, mls_standings_header_compact, mls_standings_rules)
        self.teams: dict[int, MLSTeam] = {}
        self.games: dict[int, MLSGame] = {}

    @override
    def add_team(self, name: str, short_name: str, conference: Literal["Western", "Eastern"], id: int = None) -> None:
        id = len(self.teams) if id is None else id
        self.teams[id] = MLSTeam(name, short_name, conference)

    def add_game(self, game_id: int, home_id: int, away_id: int, start_datetime: datetime, status: str, home_score: int = 0, 
                 away_score: int = 0, home_disciplinary_points: int = 0, away_disciplinary_points: int = 0) -> None:
        self.games[game_id] = MLSGame(home_id, away_id, start_datetime, status, home_score, away_score,
                                      home_disciplinary_points, away_disciplinary_points)

    @override
    def standings(self, conference: Optional[Literal["Western", "Eastern"]] = None):
        return super().standings(conference)
    
    def update_official_stats(self):
        for team in self.teams.values():
            team.reset_stats()

        for game in self.games.values():
            if game.status == "FullTime":
                self.teams[game.home_id].update_stats(True, game.home_score, game.away_score, 0)
                self.teams[game.away_id].update_stats(False, game.away_score, game.home_score, 0)
    

class NHLSeason(Season):
    @override
    def __init__(self, start_year: int, import_json: Optional[dict[Literal["games", "teams"], dict[str, int | str | dict[str, int]]]] = None) -> None:
        super().__init__(nhl_standings_header, nhl_standings_header_compact, nhl_standings_rules)
        self.teams: dict[int, NHLTeam] = {}
        self.games: dict[int, NHLGame] = {}
        self.status_mappings = {
            "Preview": "Scheduled",
            "Live": "Live",
            "Final": "Final"
        }

        if import_json is not None:
            for id, team in import_json["teams"].items():
                self.add_team(team['name'], team['short_name'], team['team_name'], team['conference'], team['division'], id)
            for id, game in import_json["games"].items():
                self.add_game(id, game['home_id'], game['away_id'], datetime.fromisoformat(team['start_datetime']), game['status'], game['home_score'],
                              game['away_score'], game['result_type'])
            self.update_official_stats()
        else:
            # TODO push this down to Team object?
            teams_params = { "season": f'{start_year}{start_year+1}' }
            teams_url = "https://statsapi.web.nhl.com/api/v1/teams"
            teams = requests.get(teams_url, params=teams_params, timeout=30).json()
            for team in teams["teams"]:
                self.add_team(team['name'], team['shortName'], team['franchise']['teamName'], team['conference']['name'], team['division']['name'], team['id'])

            schedule_params = {
                'startDate': f'{start_year}-01-01',        # YYYY-MM-DD
                'endDate': f'{start_year+1}-12-31',        # Inclusive
                'season': f'{start_year}{start_year+1}',   # Relevant season (format "20232024")
                'hydrate': 'linescore',                    # Fields to pull; eg team, linescore, metadata, seriesSummary(series)
                # 'teamId': '',                              #
                'gameType': 'R'                            # "R" = Regular season; "P" = Playoffs
            }
            # TODO push this down to Game object?
            schedule_url = "https://statsapi.web.nhl.com/api/v1/schedule"
            games = requests.get(schedule_url, params=schedule_params, timeout=30).json()
            for date in games['dates']:
                for game in date['games']:
                    result_type = "R" if game['linescore']['currentPeriod'] < 4 else game['linescore']['currentPeriodOrdinal']
                    self.add_game(game['gamePk'], game['teams']['home']['team']['id'], game['teams']['away']['team']['id'],
                                datetime.fromisoformat(game['gameDate']), self.status_mappings[game['status']['abstractGameState']],
                                game['teams']['home']['score'], game['teams']['away']['score'], result_type)

            for game in self.games.values():
                if game.status == "Final":
                    self.teams[game.home_id].update_stats(game.home_score, game.away_score, game.result_type)
                    self.teams[game.away_id].update_stats(game.away_score, game.home_score, game.result_type)

    @override
    def add_team(self, name: str, short_name: str, team_name: str, conference: Literal["Western", "Eastern"],
                 division: Literal['Central', 'Pacific', 'Metropolitan', 'Atlantic'], id: int = None) -> None:
        if ((conference == "Western" and division not in ["Central", "Pacific"]) or
            (conference == "Eastern" and division not in ["Metropolitan", "Atlantic"])):
            # TODO flesh out error message
            raise ValueError()

        id = len(self.teams) if id is None else id
        self.teams[id] = NHLTeam(name, short_name, team_name, conference, division)

    def add_game(self, game_id: int, home_id: int, away_id: int, start_datetime: datetime, status: str,
                        home_score: int = 0, away_score: int = 0, result_type: Literal["R", "OT", "SO"] = None) -> None:
        self.games[game_id] = NHLGame(home_id, away_id, start_datetime, status, home_score, away_score, result_type)

    @override
    def standings(self, conference: Optional[Literal["Western", "Eastern"]] = None, 
                  division: Optional[Literal['Central', 'Pacific', 'Metropolitan', 'Atlantic']] = None):
        return super().standings(conference, division)
    
    # TODO - update non-final games with starttime before now - for tracking live games
    # - should be an .update() method on Game object?
    # def update_official_results(self) -> None:
    #     for (id, game) in filter(lambda k,g: g.status != "Final" and g.start < datetime.now(), self.games.items()):
    #         # game_url = f"{id}"
    #         # updated_game = requests.get(game_url, )
    #         result_type = "R" if updated_game['linescore']['currentPeriod'] < 4 else updated_game['linescore']['currentPeriodOrdinal']
    #         self.add_game(updated_game['gamePk'], updated_game['teams']['home']['team']['id'], updated_game['teams']['away']['team']['id'],
    #                              datetime.fromisoformat(updated_game['gameDate']), self.status_mappings[updated_game['status']['abstractGameState']],
    #                              updated_game['teams']['home']['score'], updated_game['teams']['away']['score'], result_type)

    def update_official_stats(self):
        for team in self.teams.values():
            team.reset_stats()

        for game in self.games.values():
            if game.status == "Final":
                self.teams[game.home_id].update_stats(game.home_score, game.away_score, game.result_type)
                self.teams[game.away_id].update_stats(game.away_score, game.home_score, game.result_type)