from typing import Optional

from pydantic import BaseModel


class CivTurnInfo(BaseModel):
    """Civilization Turn info JSON Payload.

    The following is from Play by Cloud:
    value1 is the game name.
    value2 is the player name.
    value3 is the turn number.

    Play Your Damn Turn JSON contains those parameters as well as others which have self-evident names.
    """
    value1: str
    value2: str
    value3: int
    gameName: Optional[str]
    userName: Optional[str]
    round: Optional[int]
    civName: Optional[str]
    leaderName: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "value1": "Eric's Barbarian Clash Game",
                "value2": "Eric",
                "value3": "300",
                "gameName": "Eric's Barbarian Clash Game",
                "userName": "Eric",
                "round": 300,
                "civName": "Sumeria",
                "leaderName": "Gilgamesh"
            }
        }
