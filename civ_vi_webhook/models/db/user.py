import beanie


class User(beanie.Document):
    steam_username: str
    matrix_username: str | None
    index_name: str | None
