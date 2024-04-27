import datetime
import typing
from typing import TypedDict


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
    teams: list[list[Team]]


class GameStats(TypedDict):
    abil: int
    bprod: int
    edeaths: int
    ekills: int
    elitekill: int
    gt: int
    inactperiod: int
    sqkill: int
    sqlost: int
    sqprod: int
    structdmg: int
    totalcmds: int
    unitprod: int
    upg: int


class Resources(TypedDict):
    military: list[int]
    economy: list[int]


class PlayerProfile(TypedDict):
    profileId: int
    name: str
    civilization: str
    team: int
    teamName: str
    apm: int
    result: str
    _stats: GameStats
    resources: Resources
    civilizationAttrib: str


class GameSummary(TypedDict):
    gameId: int
    winReason: str
    mapName: str
    leaderboard: str
    apm: int
    players: list[PlayerProfile]


class GameRow(TypedDict):
    id: int
    map: str
    outcome: str
    end_reason: str
    duration: int
    game_mode: str
    players: str
    created_at: datetime.datetime | None


class RelicRow(TypedDict):
    id: int
    game_id: int
    name: str
    winner: str
    score: int
    created_at: datetime.datetime | None


class RelicStats(TypedDict):
    """Summary stats for relics"""
    name: str
    max_score: int
    max_score_player: int
    most_relics: int
    most_relics_player: str


def filter_dict_to_type[__T](input_dict: dict[str, typing.Any], type_: typing.Type[__T]) -> __T:
    """Picks apart an input dict and only keys specified"""
    keys = list(type_.__annotations__.keys())

    filtered_dict = {
        key: input_dict[key]
        for key in keys
        if key in input_dict
    }

    for key, value in filtered_dict.items():
        if isinstance(value, dict):
            filtered_dict[key] = filter_dict_to_type(value, type_.__annotations__[key])
        elif isinstance(value, list) and value and isinstance(value[0], dict):
            filtered_dict[key] = [
                filter_dict_to_type(item, type_.__annotations__[key].__args__[0])
                for item in value
            ]
        else:
            filtered_dict[key] = value

    return type_(filtered_dict)


def is_subdictionary(subdict: dict, main_dict: dict) -> bool:
    """Checks if a subdictionary is a subdictionary of the main dictionary.

    :param subdict: Sub-dictionary to be checked
    :param main_dict: Main dictionary to be checked
    :return: bool
    """
    for key, value in subdict.items():
        if key not in main_dict or main_dict[key] != value:
            return False
    return True
