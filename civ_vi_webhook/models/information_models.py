from pydantic import BaseModel


class Game(BaseModel):
    pass


class CurrentGames(BaseModel):
    """The response to a request for current games."""
    games: dict
