import asyncio
import json

from civ_vi_webhook.models.db import mongo_setup
from civ_vi_webhook.services.db import game_service, user_service
from civ_vi_webhook.models.db import games

async def connect_db():
    with open("creds.conf", "r") as creds:
        credentials = json.load(creds)
    # replace civ_vi_webhook with the name of the database you want, or leave it if you're OK with this name
    await mongo_setup.init_db('civ_vi_webhook',
                              username=credentials.get("username"),
                              password=credentials.get("password"),
                              dev_server=credentials.get("development_server"))


async def create_games():
    with open("most_recent_games.json", "r") as games_file:
        games_to_import = json.load(games_file)
    for game in games_to_import:
        print(games_to_import.get(game).get("time_stamp"))


async def main():
    print("Note: You should have run the player conversion first.")
    await connect_db()
    await create_games()


if __name__ == '__main__':
    asyncio.run(main())
