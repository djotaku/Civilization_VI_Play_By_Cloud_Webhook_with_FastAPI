import json
from datetime import datetime

import fastapi.responses
from fastapi import APIRouter
from starlette import status

from civ_vi_webhook import api_logger
from civ_vi_webhook.dependencies import (figure_out_base_sixty,
                                         figure_out_days)
from civ_vi_webhook.models.turns import CivTurnInfo, PYDTTurnInfo
from civ_vi_webhook.services.matrix import matrix_bot_sender as matrix_bot
from civ_vi_webhook.services.db import user_service

from ..dependencies import load_most_recent_games

router = APIRouter(tags=['Turn Endpoints'])

# ##########
# Services
# ##########
api_matrix_bot = matrix_bot.MatrixBot()


def turn_delta(games: dict, this_game: str, current_time: datetime) -> float:
    if this_game in games:
        last_turn = datetime(int(games[this_game]['time_stamp']['year']),
                             int(games[this_game]['time_stamp']['month']),
                             int(games[this_game]['time_stamp']['day']),
                             int(games[this_game]['time_stamp']['hour']),
                             int(games[this_game]['time_stamp']['minute']),
                             int(games[this_game]['time_stamp']['second']),
                             )
        return (current_time - last_turn).total_seconds()
    else:
        return 0


def get_average_time(turn_deltas: list) -> str:
    average_seconds = (sum(turn_deltas) / len(turn_deltas))
    minutes, seconds = figure_out_base_sixty(average_seconds)
    hours, minutes = figure_out_base_sixty(minutes)
    days, hours = figure_out_days(hours)
    return f"{days} days, {hours} hours, {minutes} min, {seconds:.0f}s."


@router.post('/webhook', status_code=status.HTTP_201_CREATED)
async def handle_play_by_cloud_json(play_by_cloud_game: CivTurnInfo):
    """The API endpoint for Civilization's Play By Cloud JSON data.

    The reason for the duplication checks here are in case more than one player has the webhook enabled for all turns.
    That may be desirable because, for example, right now Mac users have crashes when using the webhook.
    """
    send_message = False
    current_games = load_most_recent_games()
    turn_time = datetime.now()
    api_logger.debug(f'JSON from Play By Cloud: {play_by_cloud_game}')
    game_name = play_by_cloud_game.value1
    time_since_last_turn = turn_delta(current_games, game_name, turn_time)
    player_name = await user_service.get_matrix_name(play_by_cloud_game.value2)
    api_logger.debug(f"{player_name=} if it's the steam username then either no matrix username or not in database")
    turn_number = play_by_cloud_game.value3
    turn_deltas = []
    if game_name in current_games.keys():
        if current_games[game_name]['player_name'] != player_name:
            if previous_deltas := current_games[game_name].get('turn_deltas'):
                turn_deltas = list(previous_deltas)
            turn_deltas.append(time_since_last_turn)
            api_logger.debug("Game exists and this is *not* a duplicate")
            send_message = True
        elif current_games[game_name]['turn_number'] != turn_number:
            api_logger.debug("A turn in a two-player game was somehow missed.")
            send_message = True
        else:
            api_logger.debug("Game exists and this is a duplicate entry.")
            return fastapi.responses.JSONResponse(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                                                  content={"error": "Game exists and this is a duplicate entry."})
    else:
        turn_deltas.append(time_since_last_turn)
        api_logger.debug("New game.")
        send_message = True
    if send_message:
        average_turn_time = get_average_time(turn_deltas)
        current_games[game_name] = {'player_name': player_name,
                                    'turn_number': turn_number,
                                    'time_stamp': {'year': turn_time.year,
                                                   'month': turn_time.month,
                                                   'day': turn_time.day,
                                                   'hour': turn_time.hour,
                                                   'minute': turn_time.minute,
                                                   'second': turn_time.second},
                                    'turn_deltas': turn_deltas,
                                    'average_turn_time': average_turn_time}
        message = f"Hey, {player_name}, it's your turn in {game_name}. The game is on turn {turn_number}"
        # api_matrix_bot.main(message)  # no longer what we want to do because this is async method now
        await api_matrix_bot.send_message(message)
        with open('most_recent_games.json', 'w') as most_recent_games_file:
            json.dump(current_games, most_recent_games_file)
    return fastapi.responses.JSONResponse(status_code=status.HTTP_201_CREATED,
                                          content={"status": "Game Created"})


@router.post('/pydt', status_code=status.HTTP_201_CREATED)
async def handle_pydt_json(pydt_game: PYDTTurnInfo):
    api_logger.debug(f'JSON from PYDT: {pydt_game}')
    game_name = pydt_game.gameName
    player_name = await user_service.get_matrix_name(pydt_game.userName)
    api_logger.debug(f"{player_name=} if it's the steam username then either no matrix username or not in database")
    turn_number = pydt_game.round
    civ_name = pydt_game.civName
    leader_name = pydt_game.leaderName
    message = f"Hey, {player_name}, {leader_name} is waiting for you to command {civ_name} in {game_name}. " \
              f"The game is on turn {turn_number}"
    await api_matrix_bot.send_message(message)
    turn_time = datetime.now()
    current_games = load_most_recent_games()
    turn_deltas = []
    time_since_last_turn = turn_delta(current_games, game_name, turn_time)
    if game_name in current_games.keys():
        if previous_deltas := current_games[game_name].get('turn_deltas'):
            turn_deltas = list(previous_deltas)
        turn_deltas.append(time_since_last_turn)
    else:
        turn_deltas.append(time_since_last_turn)
    average_turn_time = get_average_time(turn_deltas)
    current_games[game_name] = {'player_name': player_name,
                                'turn_number': turn_number,
                                'time_stamp': {'year': turn_time.year,
                                               'month': turn_time.month,
                                               'day': turn_time.day,
                                               'hour': turn_time.hour,
                                               'minute': turn_time.minute,
                                               'second': turn_time.second},
                                'turn_deltas': turn_deltas,
                                'average_turn_time': average_turn_time
                                }
    with open('most_recent_games.json', 'w') as most_recent_games_file:
        json.dump(current_games, most_recent_games_file)
    return fastapi.responses.JSONResponse(status_code=status.HTTP_201_CREATED,
                                          content={"status": "Game Created"})
