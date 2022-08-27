from datetime import datetime
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
    time_stamp: Optional[TimeStamp]
    time_stamp_v2: Optional[datetime]
    all_players: set
    turn_deltas: Optional[list]
    average_turn_time: Optional[str]
    winner: Optional[str] = pydantic.Field(description="The winner of the game.")


class Game(beanie.Document):
    game_name: str
    game_info: GameInfo

    # db.source_collection.copyTo("target_collection") at the database may be the way to move games over
    class Settings:
        name = "games"
        indexes = ["game_name",
                   pymongo.IndexModel([("game_info.time_stamp.second", pymongo.DESCENDING),
                                       ],
                                      name="last_turn_date_descend")
                   ]


class CompletedGames(beanie.Document):
    """Contains a list of all completed games for endpoints."""
    completed_games: list = pydantic.Field(description="list of game IDs")


class CurrentGames(beanie.Document):
    """Contains a list of games current in progress for endpoints."""
    current_games: list = pydantic.Field(description="list of game IDs")
