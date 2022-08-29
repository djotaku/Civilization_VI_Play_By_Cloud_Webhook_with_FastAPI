import math
from pathlib import Path

import jinja_partials
from starlette.templating import Jinja2Templates

from civ_vi_webhook.models.api import games
from civ_vi_webhook.models.db import games as db_games
from civ_vi_webhook.models.db.games import Game
from civ_vi_webhook.services.db import game_service, user_service

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(Path(BASE_DIR, 'templates')))
jinja_partials.register_starlette_extensions(templates)


def figure_out_base_sixty(number: int) -> (int, int):
    """Figure out the next number up if I have more than 59 seconds or minutes."""
    return (math.floor(number / 60), number % 60) if number > 59 else (0, number)


def figure_out_days(number: int) -> (int, int):
    """Figure out number of days given a number of hours."""
    if number <= 23:
        return 0, number
    days = math.floor(number / 24)
    hours = number - (days * 24)
    return days, hours


async def db_model_to_game_model_multiple(these_games: list[db_games]) -> list[games]:
    games_to_return = []
    for game in these_games:
        game_info = await create_api_game_info(game)
        this_game = games.Game(game_name=game.game_name, game_info=game_info)
        games_to_return.append(this_game)
    return games_to_return


async def create_api_game_info(game):
    time_stamp = game.game_info.time_stamp_v2.strftime('%m-%d-%Y %H:%M:%S')
    player_name = await user_service.get_index_name_by_user_id(game.game_info.next_player_id)
    game_info = games.GameInfo(player_name=player_name, turn_number=game.game_info.turn_number,
                               game_completed=game.game_info.game_completed, time_stamp=time_stamp,
                               turn_deltas=game.game_info.turn_deltas,
                               average_turn_time=game.game_info.average_turn_time,
                               winner=game.game_info.winner)
    return game_info


async def db_model_to_game_model(game_to_complete):
    game = await game_service.get_game(game_to_complete)
    game_info = await create_api_game_info(game)
    return games.Game(game_name=game.game_name, game_info=game_info)


async def db_game_models_to_dictionary(db_games: list[Game]) -> list[dict]:
    """Convert a game from a DB Model to a dictionary for use by Jinja2"""
    games_to_return = []
    for game in db_games:
        this_game = await db_game_to_dictionary(game)
        games_to_return.append(this_game)
    return games_to_return


async def db_game_to_dictionary(game):
    time_stamp = game.game_info.time_stamp_v2.strftime('%m-%d-%Y %H:%M:%S')
    player_name = await user_service.get_index_name_by_user_id(game.game_info.next_player_id)
    return {"game_name": game.game_name, "player_name": player_name,
            "average_turn_time": game.game_info.average_turn_time, "all_players": game.game_info.all_players,
            "winner": game.game_info.winner, "turn_number": game.game_info.turn_number, "time_stamp": time_stamp}
