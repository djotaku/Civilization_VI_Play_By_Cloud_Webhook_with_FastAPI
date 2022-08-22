import asyncio
import json

from civ_vi_webhook.models.db import mongo_setup
from civ_vi_webhook.services.db.matrix_service import write_next_batch


async def connect_db():
    with open("creds.conf", "r") as creds:
        credentials = json.load(creds)
    # replace civ_vi_webhook with the name of the database you want, or leave it if you're OK with this name
    await mongo_setup.init_db('civ_vi_webhook',
                              username=credentials.get("username"),
                              password=credentials.get("password"),
                              dev_server=credentials.get("development_server"))


async def create_matrix_next_batch():
    with open("next_batch", "r") as matrix_batch:
        next_batch = matrix_batch.readline()
        await write_next_batch(next_batch)


async def main():
    await connect_db()
    await create_matrix_next_batch()


if __name__ == '__main__':
    asyncio.run(main())
