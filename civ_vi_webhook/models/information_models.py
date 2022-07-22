from pydantic import BaseModel


class TimeStamp(BaseModel):
    """A Timestamp for a turn"""
    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int


class GameInfo(BaseModel):
    """Information about a Game"""
    player_name: str
    turn_number: int
    time_stamp: TimeStamp


class Game(BaseModel):
    game_name: str
    game_info: GameInfo


class CurrentGames(BaseModel):
    """The response to a request for current games."""
    games: list[Game]
