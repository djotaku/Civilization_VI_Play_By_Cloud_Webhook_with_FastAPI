import asyncio
import json

from civ_vi_webhook.models.db import mongo_setup
from civ_vi_webhook.services.db import game_service, user_service


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
        next_player_id = await user_service.get_user_id_from_matrix_username(
            games_to_import.get(game).get("player_name"))
        turn_deltas = games_to_import.get(game).get("turn_deltas") or []
        average_turn_time = games_to_import.get(game).get("average_turn_time") or ""
        winner = games_to_import.get(game).get("winner")
        game_completed = games_to_import.get(game).get("game_completed")
        await game_service.create_game(game_name=game, player_id=next_player_id,
                                       turn_number=games_to_import.get(game).get("turn_number"),
                                       time_stamp=games_to_import.get(game).get("time_stamp"),
                                       turn_deltas=turn_deltas, average_turn_time=average_turn_time)
        if game_completed:
            await game_service.mark_game_completed(game)
        if winner:
            await game_service.add_winner_to_game(game, winner)


async def main():
    print("Note: You should have run the player conversion first.")
    await connect_db()
    await create_games()


if __name__ == '__main__':
    asyncio.run(main())
