from typing import Optional

import beanie
import pydantic
import pymongo
from beanie import PydanticObjectId
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
    next_player_id: PydanticObjectId = pydantic.Field(description="The MongoDB ID of the player whose turn it now is.")
    turn_number: int
    game_completed: bool = False
    time_stamp: TimeStamp
    all_players: set
    turn_deltas: Optional[list]
    average_turn_time: Optional[str]
    winner: Optional[str] = pydantic.Field(description="The winner of the game.")


class Game(beanie.Document):
    game_name: str
    game_info: GameInfo

    class Collection:
        name = "games"
        indexes = ["game_name",
                   pymongo.IndexModel([("game_info.time_stamp.second", pymongo.DESCENDING),
                                       ],
                                      name="last_turn_date_descend")
                   ]

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


class CompletedGames(beanie.Document):
    """Contains a list of all completed games for endpoints."""
    completed_games: list = pydantic.Field(description="list of game IDs")


class CurrentGames(beanie.Document):
    """Contains a list of games current in progress for endpoints."""
    current_games: list = pydantic.Field(description="list of game IDs")
