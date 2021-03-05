from typing import Optional
from fastapi import FastAPI, status
import json
import logging
from pydantic import BaseModel

from .services.matrix import matrix_bot_sender as matrix_bot


class CivTurnInfo(BaseModel):
    """Civilization Turn info JSON Payload.

    The following is from Play by Cloud:
    value1 is the game name.
    value2 is the player name.
    value3 is the turn number.

    Play Your Damn Turn JSON contains those parameters as well as others which have self-evident names.
    """
    value1: str
    value2: str
    value3: str
    gameName: Optional[str]
    userName: Optional[str]
    round: Optional[int]
    civName: Optional[str]
    leaderName: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "value1": "Eric's Barbarian Clash Game",
                "value2": "Eric",
                "value3": "300",
                "gameName": "Eric's Barbarian Clash Game",
                "userName": "Eric",
                "round": 300,
                "civName": "Sumeria",
                "leaderName": "Gilgamesh"
            }
        }


api_matrix_bot = matrix_bot.MatrixBot()
most_recent_games = dict()
app = FastAPI(
    title="Eric's Civilization VI Play By Cloud and PYDT Webhook server",
    description="The server acts as an endpoint for PBC and PYDT JSON then sends it to the service you configure.",
    version="0.1.0"
)

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


@app.post('/webhook', status_code=status.HTTP_201_CREATED)
def handle_play_by_cloud_json(play_by_cloud_game: CivTurnInfo):
    """The API endpoint for Civilization's Play By Cloud JSON data.

    The reason for the duplication checks here are in case more than one player has the webhook enabled for all turns.
    That may be desirable because, for example, right now Mac users have crashes when using the webhook.
    """
    logging.debug(f'JSON from Play By Cloud: {play_by_cloud_game}')
    game_name = play_by_cloud_game.value1
    player_name = player_name_to_matrix_name(play_by_cloud_game.value2)
    turn_number = play_by_cloud_game.value3
    if game_name in most_recent_games.keys():
        if most_recent_games[game_name]['player_name'] != player_name:
            logging.debug("Game exists, but this is not a duplicate")
            message = f"Hey, {player_name}, it's your turn in {game_name}. The game is on turn {turn_number}"
            api_matrix_bot.main(message)
            most_recent_games[game_name] = {'player_name': player_name, 'turn_number': turn_number}
        else:
            logging.debug("Game exists and this is a duplicate entry.")
    else:
        most_recent_games[game_name] = {'player_name': player_name, 'turn_number': turn_number}
        logging.debug("New game.")
        message = f"Hey, {player_name}, it's your turn in {game_name}. The game is on turn {turn_number}"
        api_matrix_bot.main(message)
    with open('most_recent_games.json', 'w') as most_recent_games_file:
        json.dump(most_recent_games, most_recent_games_file)


@app.post('pydt', status_code=status.HTTP_201_CREATED)
def handle_pydt_json(pydt_game: CivTurnInfo):
    logging.debug(f'JSON from PYDT: {pydt_game}')
    game_name = pydt_game.gameName
    player_name = player_name_to_matrix_name(pydt_game.userName)
    turn_number = pydt_game.round
    civ_name = pydt_game.civName
    leader_name = pydt_game.leaderName
    message = f"Hey, {player_name}, {leader_name} is waiting for you to command {civ_name} in {game_name}. " \
              f"The game is on turn {turn_number}"
    api_matrix_bot.main(message)
    most_recent_games[game_name] = {'player_name': player_name, 'turn_number': turn_number}
    with open('most_recent_games.json', 'w') as most_recent_games_file:
        json.dump(most_recent_games, most_recent_games_file)


@app.get('/recent_games')
def return_recent_games():
    """Returns the dictionary containing the games awaiting a turn.

    In the future this endpoint may change to /current_games to better reflect what it returns.
    """
    return most_recent_games
