import math
from datetime import datetime
from pathlib import Path

import jinja_partials
from starlette.templating import Jinja2Templates

from civ_vi_webhook.models.api import games
from civ_vi_webhook.services.db import game_service, user_service

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(Path(BASE_DIR, 'templates')))
jinja_partials.register_starlette_extensions(templates)


def dict_to_game_model(dictionary: dict) -> games.Game:
    """Take in a dictionary of a game and turn it into a Game model.

    Example dict:

    {"Eric's Barbarian Clash Game": {'player_name': 'Eric', 'turn_number': 300,
    'time_stamp': {'year': 2022, 'month': 7, 'day': 21, 'hour': 20, 'minute': 33,
    'second': 28}}}

    """
    game_name = list(dictionary.keys())
    game_name = game_name[0]
    time_stamp = games.TimeStamp(year=dictionary[game_name]['time_stamp']['year'],
                                 month=dictionary[game_name]['time_stamp']['month'],
                                 day=dictionary[game_name]['time_stamp']['day'],
                                 hour=dictionary[game_name]['time_stamp']['hour'],
                                 minute=dictionary[game_name]['time_stamp']['minute'],
                                 second=dictionary[game_name]['time_stamp']['second'])
    game_info = games.GameInfo(player_name=dictionary[game_name]['player_name'],
                               turn_number=dictionary[game_name]['turn_number'],
                               game_completed=dictionary[game_name].get('game_completed'),
                               time_stamp=time_stamp,
                               turn_deltas=dictionary[game_name].get('turn_deltas'),
                               average_turn_time=dictionary[game_name].get('average_turn_time'))
    return games.Game(game_name=game_name, game_info=game_info)


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


def return_time(time_difference) -> (int, int, int, int):
    """Return time in a useful manner."""
    days = time_difference.days
    seconds = time_difference.seconds
    minutes, seconds = figure_out_base_sixty(seconds)
    hours, minutes = figure_out_base_sixty(minutes)
    days_plus, hours = figure_out_days(hours)
    days += days_plus
    return days, hours, minutes, seconds


def determine_time_delta(year, month, day, hour, minute, second) -> str:
    time_of_question = datetime.now()
    time_of_turn = datetime(year, month, day, hour, minute, second)
    difference = time_of_question - time_of_turn
    days, hours, minutes, seconds = return_time(difference)
    return f"It's been {days} days {hours} hours {minutes} minutes {seconds} seconds since the last turn."


def format_year_to_number(time_stamp: dict) -> int:
    """Take in a dict with time stamp and convert to a number"""
    return int(
        f"{time_stamp['year']}{time_stamp['month']:0>2d}{time_stamp['day']:0>2d}{time_stamp['hour']:0>2d}{time_stamp['minute']:0>2d}{time_stamp['second']:0>2d}")


async def db_model_to_game_model_multiple(these_games):
    games_to_return = []
    for game in these_games:
        time_stamp = games.TimeStamp(year=game.game_info.time_stamp.year,
                                     month=game.game_info.time_stamp.month,
                                     day=game.game_info.time_stamp.day,
                                     hour=game.game_info.time_stamp.hour,
                                     minute=game.game_info.time_stamp.minute,
                                     second=game.game_info.time_stamp.second)
        player_name = await user_service.get_index_name_by_user_id(game.game_info.next_player_id)
        game_info = games.GameInfo(player_name=player_name, turn_number=game.game_info.turn_number,
                                   game_completed=game.game_info.game_completed, time_stamp=time_stamp,
                                   turn_deltas=game.game_info.turn_deltas,
                                   average_turn_time=game.game_info.average_turn_time,
                                   winner=game.game_info.winner)
        this_game = games.Game(game_name=game.game_name, game_info=game_info)
        games_to_return.append(this_game)
    return games_to_return


async def db_model_to_game_model(game_to_complete):
    game = await game_service.get_game(game_to_complete)
    time_stamp = games.TimeStamp(year=game.game_info.time_stamp.year,
                                 month=game.game_info.time_stamp.month,
                                 day=game.game_info.time_stamp.day,
                                 hour=game.game_info.time_stamp.hour,
                                 minute=game.game_info.time_stamp.minute,
                                 second=game.game_info.time_stamp.second)
    player_name = await user_service.get_index_name_by_user_id(game.game_info.next_player_id)
    game_info = games.GameInfo(player_name=player_name, turn_number=game.game_info.turn_number,
                               game_completed=game.game_info.game_completed, time_stamp=time_stamp,
                               turn_deltas=game.game_info.turn_deltas,
                               average_turn_time=game.game_info.average_turn_time,
                               winner=game.game_info.winner)
    return games.Game(game_name=game.game_name, game_info=game_info)
