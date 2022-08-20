import asyncio
import json

from civ_vi_webhook.models.db import mongo_setup
from civ_vi_webhook.services.db.user_service import create_user

async def connect_db():
    with open("creds.conf", "r") as creds:
        credentials = json.load(creds)
    # replace civ_vi_webhook with the name of the database you want, or leave it if you're OK with this name
    await mongo_setup.init_db('civ_vi_webhook',
                              username=credentials.get("username"),
                              password=credentials.get("password"))


async def create_players():
    with open("player_names.conf", "r") as players:
        player_identities = json.load(players)
        # I'm going to go with matrix here because if anyone has been using my code up to this point, they'll
        # only have been able to support Matrix (as opposed to Discord or other services)
        for steam_username, matrix_username in player_identities["matrix"].items():
            index_name = player_identities.get("preferred_names").get(steam_username)
            # print(f"{steam_username=} known as {matrix_username=} and {index_name=}")
            await create_user(steam_username, matrix_username=matrix_username, index_name=index_name)


async def main():
    await connect_db()
    await create_players()

if __name__ == '__main__':
    asyncio.run(main())
