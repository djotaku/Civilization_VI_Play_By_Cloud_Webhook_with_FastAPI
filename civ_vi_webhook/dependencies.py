import json
from starlette.templating import Jinja2Templates
from pathlib import Path
import jinja_partials

from civ_vi_webhook import api_logger
from civ_vi_webhook.models import games

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(Path(BASE_DIR, 'templates')))
jinja_partials.register_starlette_extensions(templates)


def load_most_recent_games() -> dict:
    """Loads in the most recent games from the JSON file."""
    recent_games = {}
    try:
        with open('most_recent_games.json', 'r') as file:
            recent_games = json.load(file)
            api_logger.debug("current_games file loaded.")
    except FileNotFoundError:
        api_logger.warning("Prior JSON file not found. If this is your first run, this is OK.")
    return recent_games


def load_player_names() -> dict:
    """If player names have been defined, load them in."""
    try:
        with open('player_names.conf', 'r') as file:
            player_names = json.load(file)
            api_logger.debug("Player Conversion file loaded.")
    except FileNotFoundError:
        api_logger.warning("No Player Conversion file loaded. Messages will use Steam account names.")
    return player_names


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
                               time_stamp=time_stamp)
    return games.Game(game_name=game_name, game_info=game_info)
