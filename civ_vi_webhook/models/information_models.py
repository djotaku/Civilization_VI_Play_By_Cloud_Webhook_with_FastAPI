from pydantic import BaseModel

from civ_vi_webhook.models.games import Game


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


class GameCounts(BaseModel):
    """A model representing the number of games tracked on by the API."""
    total_games: int
