from pydantic import BaseModel

from typing import Optional


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
    game_completed: Optional[bool]
    time_stamp: TimeStamp
    turn_deltas: Optional[list]
    average_turn_time: Optional[str]
    winner: Optional[str]


class Game(BaseModel):
    game_name: str
    game_info: GameInfo

    class Config:
        schema_extra = {
            "example": {
                "game_name": "Eric's Barbarian Clash Game",
                "game_info": {
                    "player_name": "Eric",
                    "turn_number": 300,
                    "game_completed": False,
                    "time_stamp": {
                        "year": 2022,
                        "month": 7,
                        "day": 21,
                        "hour": 20,
                        "minute": 33,
                        "second": 28
                    },
                    "turn_deltas": [24, 6677, 34],
                    "average_turn_time": "0 days, 0 hours, 4 min, 12s.",
                    "winner": "Eric"
                }
            }
        }
