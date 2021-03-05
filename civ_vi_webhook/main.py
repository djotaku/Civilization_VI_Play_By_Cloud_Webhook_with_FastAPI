from typing import Optional
from fastapi import FastAPI
import json
import logging
from pydantic import BaseModel

from .services.matrix import matrix_bot_sender as matrix_bot


class PlayByCloud(BaseModel):
    """Play by Cloud JSON.

    value1 is the game name.
    value2 is the player name.
    value3 is the turn number.
    """
    value1: str
    value2: str
    value3: str


flask_matrix_bot = matrix_bot.MatrixBot()
most_recent_games = dict()
app = FastAPI()

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s- %(asctime)s - %(message)s')

# ##########################################
# This should be added to FastAPI's Startup
# ##########################################

try:
    with open('most_recent_games.json', 'r') as file:
        most_recent_games = json.load(file)
        logging.debug("JSON file loaded.")
except FileNotFoundError:
    logging.warning("Prior JSON file not found. If this is your first run, this is OK.")

# ###############
# End of Startup
# ###############


def player_name_to_matrix_name(player_name: str) -> str:
    if player_name == "One Oh Eight":
        return "Dan"
    elif player_name == "TheDJOtaku":
        return "Eric"
    elif player_name == "Wedge":
        return "David"
    else:
        return player_name


@app.post('/webhook')
def respond(play_by_cloud_game: PlayByCloud):
    """The API endpoint for Civilization's Play By Cloud JSON data."""
    logging.debug(f'JSON from Play By Cloud: {play_by_cloud_game}')
    game_name = play_by_cloud_game.value1
    player_name = player_name_to_matrix_name(play_by_cloud_game.value2)
    turn_number = play_by_cloud_game.value3
    if game_name in most_recent_games.keys():
        if most_recent_games[game_name]['player_name'] != player_name:
            logging.debug("Game exists, but this is not a duplicate")
            message = f"Hey, {player_name}, it's your turn in {game_name}. The game is on turn {turn_number}"
            flask_matrix_bot.main(message)
            most_recent_games[game_name] = {'player_name': player_name, 'turn_number': turn_number}
        else:
            logging.debug("Game exists and this is a duplicate entry.")
    else:
        most_recent_games[game_name] = {'player_name': player_name, 'turn_number': turn_number}
        logging.debug("New game.")
        message = f"Hey, {player_name}, it's your turn in {game_name}. The game is on turn {turn_number}"
        flask_matrix_bot.main(message)
    with open('most_recent_games.json', 'w') as most_recent_games_file:
        json.dump(most_recent_games, most_recent_games_file)


@app.get('/recent_games')
def return_recent_games():
    """Returns the dictionary containing the games awaiting a turn.

    In the future this endpoint may change to /outstanding_games to better reflect what it returns.
    """
    return most_recent_games
