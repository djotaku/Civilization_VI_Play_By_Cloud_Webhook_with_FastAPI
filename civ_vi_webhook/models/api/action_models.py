from pydantic import BaseModel

from .games import Game


class DeletedGame(BaseModel):
    deleted_game_name: str


class CompletedGame(BaseModel):
    """Return model for a game marked as completed."""
    completed_game: Game

    class Config:
        schema_extra = {
            "example": {
                "game_name": "Eric's Barbarian Clash Game",
                "game_info": {
                    "player_name": "Eric",
                    "turn_number": 300,
                    "game_completed": True,
                    "time_stamp": {
                        "year": 2022,
                        "month": 7,
                        "day": 21,
                        "hour": 20,
                        "minute": 33,
                        "second": 28
                    }
                }
            }
        }


class Error(BaseModel):
    message: str
