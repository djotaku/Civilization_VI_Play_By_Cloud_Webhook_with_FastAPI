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


async def get_matrix_name(steam_username: str) -> str:
    """Pass in a steam username and get a matrix username, if defined.

    Otherwise, return the Steam username.
    """
    user = await User.find_one(User.steam_username == steam_username)
    if user and (matrix_username := user.matrix_username):
        return matrix_username
    else:
        return steam_username  # no matrix name found or user not in database
