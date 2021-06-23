from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Query, status
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


def load_most_recent_games() -> dict:
    """Loads in the most recent games from the JSON file.

    I have moved this to a function so it can be mocked out for testing."""
    games = {}
    try:
        with open('most_recent_games.json', 'r') as file:
            games = json.load(file)
            api_logger.debug("current_games file loaded.")
    except FileNotFoundError:
        api_logger.warning("Prior JSON file not found. If this is your first run, this is OK.")
    return games


def load_player_names() -> dict:
    """If player names have been defined, load them in."""
    try:
        with open('player_names.conf', 'r') as file:
            player_names = json.load(file)
            api_logger.debug("Player Conversion file loaded.")
    except FileNotFoundError:
        api_logger.warning("No Player Conversion file loaded. Messages will use Steam account names.")
    return player_names


# ##########
# Services
# ##########
api_matrix_bot = matrix_bot.MatrixBot()

# ##########
# Configs
# ##########

player_name_conversions = load_player_names()

current_games = load_most_recent_games()
app = FastAPI(
    title="Eric's Civilization VI Play By Cloud and PYDT Webhook server",
    description="The server acts as an endpoint for PBC and PYDT JSON then sends it to the service you configure.",
    version="0.2.0"
)

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s- api - %(asctime)s - %(message)s')
api_logger = logging.getLogger("api server")
api_logger.setLevel(logging.DEBUG)


# #############
# end Configs #
# #############

def player_name_to_matrix_name(player_name: str) -> str:
    if not player_name_conversions:
        return player_name
    api_logger.debug("player_name_conversions exists")
    if player_name not in player_name_conversions['matrix'].keys():
        return player_name
    api_logger.debug(f"player name is found in the dictionary keys. It is {player_name}")
    return player_name_conversions['matrix'][player_name]


@app.post('/webhook', status_code=status.HTTP_201_CREATED)
def handle_play_by_cloud_json(play_by_cloud_game: CivTurnInfo):
    """The API endpoint for Civilization's Play By Cloud JSON data.

    The reason for the duplication checks here are in case more than one player has the webhook enabled for all turns.
    That may be desirable because, for example, right now Mac users have crashes when using the webhook.
    """
    send_message = False
    api_logger.debug(f'JSON from Play By Cloud: {play_by_cloud_game}')
    turn_time = datetime.now()
    game_name = play_by_cloud_game.value1
    player_name = player_name_to_matrix_name(play_by_cloud_game.value2)
    turn_number = play_by_cloud_game.value3
    if game_name in current_games.keys():
        if current_games[game_name]['player_name'] != player_name:
            api_logger.debug("Game exists, but this is not a duplicate")
            send_message = True
        elif current_games[game_name]['turn_number'] != turn_number:
            api_logger.debug("A turn in a two-player game was somehow missed.")
            send_message = True
        else:
            api_logger.debug("Game exists and this is a duplicate entry.")
            raise HTTPException(status_code=429, detail="Game exists and this is a duplicate entry.")
    else:
        api_logger.debug("New game.")
        send_message = True
    if send_message:
        current_games[game_name] = {'player_name': player_name,
                                    'turn_number': turn_number,
                                    'time_stamp': {'year': turn_time.year,
                                                   'month': turn_time.month,
                                                   'day': turn_time.day,
                                                   'hour': turn_time.hour,
                                                   'minute': turn_time.minute,
                                                   'second': turn_time.second}}
        message = f"Hey, {player_name}, it's your turn in {game_name}. The game is on turn {turn_number}"
        api_matrix_bot.main(message)
        with open('most_recent_games.json', 'w') as most_recent_games_file:
            json.dump(current_games, most_recent_games_file)


@app.post('/pydt', status_code=status.HTTP_201_CREATED)
def handle_pydt_json(pydt_game: CivTurnInfo):
    api_logger.debug(f'JSON from PYDT: {pydt_game}')
    game_name = pydt_game.gameName
    player_name = player_name_to_matrix_name(pydt_game.userName)
    turn_number = pydt_game.round
    civ_name = pydt_game.civName
    leader_name = pydt_game.leaderName
    message = f"Hey, {player_name}, {leader_name} is waiting for you to command {civ_name} in {game_name}. " \
              f"The game is on turn {turn_number}"
    api_matrix_bot.main(message)
    turn_time = datetime.now()
    current_games[game_name] = {'player_name': player_name,
                                'turn_number': turn_number,
                                'time_stamp': {'year': turn_time.year,
                                               'month': turn_time.month,
                                               'day': turn_time.day,
                                               'hour': turn_time.hour,
                                               'minute': turn_time.minute,
                                               'second': turn_time.second}}
    with open('most_recent_games.json', 'w') as most_recent_games_file:
        json.dump(current_games, most_recent_games_file)


@app.get('/current_games')
def return_current_games(player_to_blame: Optional[str] = Query(None,
                                                                title="Player to Blame",
                                                                description="To see how many games outstanding.")):
    """Returns the dictionary containing the games awaiting a turn.

    If a player name is passed, it will return the games that player has outstanding.

    Otherwise it will return a list of all the games outstanding.
    """
    if player_to_blame:
        does_player_exist = any(
            player_to_blame in current_games[games].get('player_name')
            for games in current_games.keys())

        if does_player_exist:
            return {game: game_attributes for (game, game_attributes) in current_games.items()
                    if current_games[game].get('player_name') == player_to_blame}
        else:
            raise HTTPException(status_code=404, detail="Player not found")
    return current_games


@app.get('/total_number_of_games')
def return_total_number_of_games():
    """Returns the total number of games the API knows about."""
    return len(current_games)


@app.delete('/delete_game')
def delete_game(game_to_delete: str = Query(None,
                                            title="Game to Delete",
                                            description="The name of the game to delete")):
    """Delete the game passed to this endpoint."""
    if game_to_delete not in current_games.keys():
        raise HTTPException(status_code=404, detail="Item not found")
    deleted_game = current_games.pop(game_to_delete)
    with open('most_recent_games.json', 'w') as most_recent_games_file:
        json.dump(current_games, most_recent_games_file)
    api_logger.debug(f"Deleted {deleted_game}")
