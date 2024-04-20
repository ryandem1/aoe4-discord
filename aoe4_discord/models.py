from typing import TypedDict, List, Dict, Any


class Player(TypedDict):
    profile_id: int
    name: str
    result: str
    civilization: str
    civilization_randomized: bool
    rating: int
    rating_diff: int
    mmr: int
    mmr_diff: int
    input_type: str


class Team(TypedDict):
    player: Player


class Game(TypedDict):
    game_id: int
    started_at: str
    updated_at: str
    duration: int
    map: str
    kind: str
    leaderboard: str
    mmr_leaderboard: str
    season: int
    server: str
    patch: int
    average_rating: int
    average_rating_deviation: int
    average_mmr: int
    average_mmr_deviation: int
    ongoing: bool
    just_finished: bool
    teams: List[List[Team]]
