import beanie
from typing import Optional


class User(beanie.Document):
    steam_username: str
    matrix_username: Optional[str]
    index_name: Optional[str]

    class Settings:
        name = "users"
