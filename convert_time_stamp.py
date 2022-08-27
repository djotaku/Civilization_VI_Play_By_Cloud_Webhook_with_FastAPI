import asyncio
import json

from civ_vi_webhook.models.db import mongo_setup
from civ_vi_webhook.services.db import game_service


async def connect_db():
    with open("creds.conf", "r") as creds:
        credentials = json.load(creds)
    # replace civ_vi_webhook with the name of the database you want, or leave it if you're OK with this name
    await mongo_setup.init_db('civ_vi_webhook',
                              username=credentials.get("username"),
                              password=credentials.get("password"),
                              dev_server=credentials.get("development_server"))


async def convert_games():
    await game_service.convert_to_new_time_stamp()


async def main():
    await connect_db()
    await convert_games()


if __name__ == '__main__':
    asyncio.run(main())
