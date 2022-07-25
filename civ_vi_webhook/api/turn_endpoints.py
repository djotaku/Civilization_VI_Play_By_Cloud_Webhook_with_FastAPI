import json
from datetime import datetime

import fastapi.responses
from fastapi import HTTPException, APIRouter
from starlette import status

from civ_vi_webhook import api_logger
from civ_vi_webhook.dependencies import load_player_names
from civ_vi_webhook.models.turns import CivTurnInfo, PYDTTurnInfo
from civ_vi_webhook.services.matrix import matrix_bot_sender as matrix_bot
from ..dependencies import load_most_recent_games

# ##########
# Services
# ##########
api_matrix_bot = matrix_bot.MatrixBot()

player_name_conversions = load_player_names()


def player_name_to_matrix_name(player_name: str) -> str:
    if not player_name_conversions:
        return player_name
    api_logger.debug("player_name_conversions exists")
    if player_name not in player_name_conversions['matrix'].keys():
        return player_name
    api_logger.debug(f"player name is found in the dictionary keys. It is {player_name}")
    return player_name_conversions['matrix'][player_name]


router = APIRouter(tags=['Turn Endpoints'])


@router.post('/webhook', status_code=status.HTTP_201_CREATED)
def handle_play_by_cloud_json(play_by_cloud_game: CivTurnInfo):
    """The API endpoint for Civilization's Play By Cloud JSON data.

    The reason for the duplication checks here are in case more than one player has the webhook enabled for all turns.
    That may be desirable because, for example, right now Mac users have crashes when using the webhook.
    """
    send_message = False
    current_games = load_most_recent_games()
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
            return fastapi.responses.JSONResponse(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                                                  content={"error": "Game exists and this is a duplicate entry."})
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
    return fastapi.responses.JSONResponse(status_code=status.HTTP_201_CREATED,
                                          content={"status": "Game Created"})


@router.post('/pydt', status_code=status.HTTP_201_CREATED)
def handle_pydt_json(pydt_game: PYDTTurnInfo):
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
    current_games = load_most_recent_games()
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
    return fastapi.responses.JSONResponse(status_code=status.HTTP_201_CREATED,
                                          content={"status": "Game Created"})
