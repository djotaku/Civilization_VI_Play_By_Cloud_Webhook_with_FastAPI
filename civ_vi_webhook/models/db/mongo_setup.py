import beanie
import motor.motor_asyncio

from .user import User
from .games import Game, CompletedGames, CurrentGames


async def init_db(database: str, username: str, password: str):
    # don't forget to authorize your IP address first if using Atlas
    # If you're not me, you'll need to edit the part after the @
    conn_str = f'mongodb+srv://{username}:{password}@cluster0.r5cyltu.mongodb.net/?retryWrites=true&w=majority'
    db_client = motor.motor_asyncio.AsyncIOMotorClient(conn_str)
    await beanie.init_beanie(db_client[database], document_models=[User, Game, CompletedGames, CurrentGames])
