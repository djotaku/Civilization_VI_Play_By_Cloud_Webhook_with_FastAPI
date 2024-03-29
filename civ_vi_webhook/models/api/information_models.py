from pydantic import BaseModel

from civ_vi_webhook.models.api.games import Game


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
                            "game_completed": False,
                            "time_stamp": "08-26-2022 16:24:40"
                        }
                    },
                    {
                        "game_name": "Dan's Crazy Game",
                        "game_info": {
                            "player_name": "David",
                            "turn_number": 5,
                            "game_completed": True,
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
    current_games: int
    completed_games: int
