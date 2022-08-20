from ...models.db.user import User


async def create_user(steam_username: str, **kwargs) -> User:
    """Create the user in the Mongo database.
    Any optional attributes should be in the kwargs.
    """
    user = User(steam_username=steam_username,
                matrix_username=kwargs.get("matrix_username"),
                index_name=kwargs.get("index_name"))
    await user.save()
    return user
