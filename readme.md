# Playoff odds calculator

## Concept

A website that keeps track of official and live (accounting for in-progress games) standings for a variety of sports/leagues, with various playoff outcomes calculated based on each.

### User-facing calculations

- Playoff spot odds
- Winning/Losing magic numbers
- Tiebreakers
- Strength of schedule
- Most important games
- What if?
- Clinching options
- Elimination options

## Objects

### League
- Standings rules (tiebreakers)
- Some leagues use coin flips
- Games (schedule/records)
- Teams (conferences/divisions)
- Playoff rules


### Team
- Name
- Statistics represented in standings, derived from Games
- Currently playing (to look up for live standings/odds)
- Data source ID


### Game
- State
  - Scheduled
    - Start time
  - In Progress
    - Game clock
  - Complete
  - Postponed/rescheduled/suspended
  - Intermission/halftime?
- Score
- Home team
- Away team
- Sport/league-specific, standings-relevant stats
  - MLS
    - Home/away goals for/against
    - Disciplinary points
  - NHL
    - Goals for/against
- Data source ID

## Mechanics

### Preseason

- Pull in schedules once they're live, as Games

### During season

#### Tracking games
- Around midnight each day, use Game Start Time to pull list of IDs for day's games
- Shortly before each Game's Start Time, spawn a worker to periodically ping for current game state until state becomes Complete/Final
  - Pull values we care about (keeping track of in Game) and compare to known state
    - If changes, update Game
  - Rate limit based on number of live Games/workers
- Periodically update Live Standings based on known Game states

#### Calculating playoff odds
- Method 1: Naive tallying of outcomes
  - Each game's possible outcome (eg A def B, B def A, tie, A def B (OT), B def A (OT), A def B (SO), B def A (SO)) is simulated
  - Final standings of each path calculated
  - Probabilities calculated as number of final states with Team X in Position >= Y
- Method 2: Weighting of outcome type
  - Same as above, but eg shootouts are weighted to historical probabilities with equal odds of victory
- Method 3: Full weighting of potential outcomes
  - Same as above, with added odds of victory based on team performance, loosely defined
  - Requires a good deal of planning/analysis to decide on weighting algo
  - To consider: Messi effects, etc

## Gameplan

1. Pick a league to start with (done; NHL)
2. Create Game/Team/League objects, relationships to get from games to standings (done)
3. Create methods to pull in real historical data (in progress)
4. Create methods to pull in and parse live game data into official/live calculations
5. Create methods to simulate unplayed games
6. Create methods for additional probabilistic calculations listed above
7. Create systems for polling of live games, intelligent handling of off-days, etc
8. Create wrappers for league data sources
9. Create test suite
10. Create front-end