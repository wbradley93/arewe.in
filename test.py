from classes.league import NHLLeague, MLSLeague
from classes.team import NHLTeam, MLSTeam
from classes.game import NHLGame, MLSGame
from utils.standings_formatter import print_standings
import datetime, requests

# nhl = NHLLeague()

# # blues = NHLTeam("St. Louis Blues", 'Western', 'Central')
# # wild = NHLTeam("Minnesota Wild", 'Western', 'Central')

# nhl.add_team("St. Louis Blues", "St. Louis", "Blues", "Western", "Central")
# nhl.add_team("Minnesota Wild", "Minnesota", "Wild", "Western", "Central")

# # blues 3 : wild 0 (r)
# nhl.games.append(NHLGame(0, 0, 1, datetime.datetime.now(), "Final", 3, 0, "R"))
# # blues 1 : wild 2 (so)
# nhl.games.append(NHLGame(0, 1, 0, datetime.datetime.now(), "Final", 2, 1, "SO"))
# # blues 2 : wild 0 (r)
# nhl.games.append(NHLGame(0, 0, 1, datetime.datetime.now(), "Final", 2, 0, "R"))
# # blues 2 : wild 0 (r)
# nhl.games.append(NHLGame(0, 0, 1, datetime.datetime.now(), "Final", 2, 0, "R"))
# # blues 2 : wild 0 (r)
# nhl.games.append(NHLGame(0, 0, 1, datetime.datetime.now(), "Final", 2, 0, "R"))
# # blues 2 : wild 0 (r)
# nhl.games.append(NHLGame(0, 0, 1, datetime.datetime.now(), "Final", 2, 0, "R"))
# # blues 1 : wild 0 (ot)
# nhl.games.append(NHLGame(0, 1, 0, datetime.datetime.now(), "Final", 1, 0, "OT"))
# # blues 0 : wild 1 (ot)
# nhl.games.append(NHLGame(0, 1, 0, datetime.datetime.now(), "Final", 1, 0, "OT"))
# # blues 0 : wild 1 (r)
# nhl.games.append(NHLGame(0, 0, 1, datetime.datetime.now(), "Final", 0, 1, "R"))
# # blues 0 : wild 4 (r)
# nhl.games.append(NHLGame(0, 0, 1, datetime.datetime.now(), "Final", 0, 4, "R"))

# nhl.update_official_stats()

# print_standings(nhl.get_standings_header(True), [t.standings_line() for t in nhl.standings("division", conference="Western", division="Central")])

# ===============================================================

# url_base = "https://statsapi.web.nhl.com/api/v1/"
# url_teams = url_base + "teams"
# url_schedule = url_base + "schedule"

# schedule_params = {
#     'startDate': '2023-01-01',      # YYYY-MM-DD
#     'endDate': '2024-12-31',        # Inclusive
#     'season': '20232024',           #
#     'hydrate': 'linescore',         # fields to pull; eg team, linescore, metadata, seriesSummary(series)
#     # 'teamId': '',                   # 
#     'gameType': 'R'                 # "R" = Regular season; "P" = Playoffs
# }

# realNhl = NHLLeague()

# teams = requests.get(url_teams).json()
# for team in teams["teams"]:
#     realNhl.add_team(team['name'], team['shortName'], team['franchise']['teamName'], team['conference']['name'], team['division']['name'], team['id'])

# periods = {
#     0: "Pregame",
#     1: "1st",
#     2: "2nd",
#     3: "3rd",
#     4: "OT",
#     5: "SO"
# }
# dtypes = ['t', 'i', 'i', 'i', 'i', 'i', 'f', 'i', 'i', 'i', 'i', 't']

# games = requests.get(url_schedule, params=schedule_params).json()
# for date in games['dates']:
#     for game in date['games']:
#         result_type = "R" if game['linescore']['currentPeriod'] < 4 else game['linescore']['currentPeriodOrdinal']

#         realNhl.add_game(game['gamePk'], game['teams']['home']['team']['id'], game['teams']['away']['team']['id'], datetime.datetime.fromisoformat(game['gameDate']), 
#                          game['status']['abstractGameState'], game['teams']['home']['score'], game['teams']['away']['score'], result_type)

# realNhl.update_official_stats()

# print("Western | Central")
# print_standings(realNhl.get_standings_header(True), [t.standings_line() for t in realNhl.standings("division", conference="Western", division="Central")], dtypes)
# print("Western | Pacific")
# print_standings(realNhl.get_standings_header(True), [t.standings_line() for t in realNhl.standings("division", conference="Western", division="Pacific")], dtypes)
# print("Eastern | Atlantic")
# print_standings(realNhl.get_standings_header(True), [t.standings_line() for t in realNhl.standings("division", conference="Eastern", division="Atlantic")], dtypes)
# print("Eastern | Metropolitan")
# print_standings(realNhl.get_standings_header(True), [t.standings_line() for t in realNhl.standings("division", conference="Eastern", division="Metropolitan")], dtypes)

# ===============================================================

teams_url = "https://sportapi.mlssoccer.com/api/standings/live?isLive=true&seasonId=2023&competitionId=98"
games_url = "https://sportapi.mlssoccer.com/api/matches?culture=en-us&dateFrom=2023-01-01&dateTo=2023-12-02&competition=98&matchType=Regular&excludeSecondaryTeams=true"

mls = MLSLeague()

teams = requests.get(teams_url).json()

for team in teams:
    mls.add_team(team['club']['fullName'], team['club']['shortName'], team['group_id']+"ern", team['club']['optaId'])

games = requests.get(games_url).json()

for game in games:
    match_url = f"https://stats-api.mlssoccer.com/v1/clubs/matches?=&match_game_id={game['optaId']}&include=club&include=match"
    match_details = requests.get(match_url).json()

    if match_details[0]['side'] == "home":
        home_score = match_details[0]['score']
        away_score = match_details[1]['score']
    else:
        home_score = match_details[1]['score']
        away_score = match_details[0]['score']

    mls.add_game(game['optaId'], game['home']['optaId'], game['away']['optaId'], datetime.datetime.fromisoformat(game['matchDate']), 
                 match_details[0]['match']['period'], home_score, away_score)
    
mls.update_official_stats()

print("Western")
print_standings(mls.get_standings_header(True), [t.standings_line() for t in mls.standings(conference="Western")])
print("Eastern")
print_standings(mls.get_standings_header(True), [t.standings_line() for t in mls.standings(conference="Eastern")])