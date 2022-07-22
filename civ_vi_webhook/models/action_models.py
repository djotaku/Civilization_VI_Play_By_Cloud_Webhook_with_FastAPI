from pydantic import BaseModel

from .games import Game


class DeletedGame(BaseModel):
    deleted_game: Game
