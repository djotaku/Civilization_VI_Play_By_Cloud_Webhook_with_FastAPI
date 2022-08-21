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


async def get_user(steam_username: str) -> User:
    """Return a user model."""
    user = await User.find_one(User.steam_username == steam_username)
    if not user:
        await create_user(steam_username)
    return user


async def get_user_id_from_matrix_username(matrix_username: str) -> str:
    """Return the user id as a string based on the matrix_username."""
    user = await User.find_one(User.matrix_username == matrix_username)
    return str(user.id) if user else ""


async def get_index_name_by_user_id(user_id) -> str:
    """Return the index name by user_id"""
    user = await User.find_one(User.id == user_id)
    return user.index_name


async def get_all_index_names() -> list[str]:
    users = await User.find().to_list()
    return [user.index_name for user in users if user.index_name is not None]
