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

    class Config:
        schema_extra = {
            "example": {
                "games": [
                    {
                        "game_name": "Eric's Barbarian Clash Game",
                        "game_info": {
                            "player_name": "Eric",
                            "turn_number": 300,
                            "time_stamp": {
                                "year": 2022,
                                "month": 7,
                                "day": 21,
                                "hour": 20,
                                "minute": 33,
                                "second": 28
                            }
                        }
                    },
                    {
                        "game_name": "Dan's Crazy Game",
                        "game_info": {
                            "player_name": "David",
                            "turn_number": 5,
                            "time_stamp": {
                                "year": 2022,
                                "month": 7,
                                "day": 22,
                                "hour": 12,
                                "minute": 11,
                                "second": 39
                            }
                        }
                    }
                ]
            }
        }
