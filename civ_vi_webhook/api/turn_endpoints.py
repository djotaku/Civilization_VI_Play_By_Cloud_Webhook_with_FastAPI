import json
from datetime import datetime

import fastapi.responses
from fastapi import APIRouter
from starlette import status

from civ_vi_webhook import api_logger
from civ_vi_webhook.dependencies import (figure_out_base_sixty,
                                         figure_out_days)
from civ_vi_webhook.models.api.turns import CivTurnInfo, PYDTTurnInfo
from civ_vi_webhook.services.matrix import matrix_bot_sender as matrix_bot
from civ_vi_webhook.services.db import user_service, game_service

router = APIRouter(tags=['Turn Endpoints'])

# ##########
# Services
# ##########
api_matrix_bot = matrix_bot.MatrixBot()


async def turn_delta(this_game: str, current_time: datetime) -> float:
    if await game_service.check_for_game(this_game):
        game = await game_service.get_game(this_game)
        last_turn = datetime(game.game_info.time_stamp.year,
                             game.game_info.time_stamp.month,
                             game.game_info.time_stamp.day,
                             game.game_info.time_stamp.hour,
                             game.game_info.time_stamp.minute,
                             game.game_info.time_stamp.second)
        return (current_time - last_turn).total_seconds()
    else:
        return 0


def get_average_time(turn_deltas: list) -> str:
    average_seconds = (sum(turn_deltas) / len(turn_deltas))
    minutes, seconds = figure_out_base_sixty(average_seconds)
    hours, minutes = figure_out_base_sixty(minutes)
    days, hours = figure_out_days(hours)
    return f"{days} days, {hours} hours, {minutes} min, {seconds:.0f}s."


async def create_or_update_game(game_name: str, time_since_last_turn: float, player_id,
                                turn_number: int, turn_time: datetime):
    """Create or update a game in the database."""
    turn_deltas = []
    continuing_game: bool = await game_service.check_for_game(game_name)
    time_stamp = {'year': turn_time.year, 'month': turn_time.month, 'day': turn_time.day,
                  'hour': turn_time.hour, 'minute': turn_time.minute, 'second': turn_time.second}
    if continuing_game:
        game = await game_service.get_game(game_name)
        turn_deltas = game.game_info.turn_deltas
        turn_deltas.append(time_since_last_turn)
        average_turn_time = get_average_time(turn_deltas)
        await game_service.update_game(game_name=game_name, player_id=player_id, turn_number=turn_number,
                                       time_stamp=time_stamp, turn_deltas=turn_deltas,
                                       average_turn_time=average_turn_time)
    else:
        turn_deltas.append(time_since_last_turn)
        average_turn_time = get_average_time(turn_deltas)
        await game_service.create_game(game_name=game_name, player_id=player_id, turn_number=turn_number,
                                       time_stamp=time_stamp, turn_deltas=turn_deltas,
                                       average_turn_time=average_turn_time)


@router.post('/webhook', status_code=status.HTTP_201_CREATED)
async def handle_play_by_cloud_json(play_by_cloud_game: CivTurnInfo):
    """The API endpoint for Civilization's Play By Cloud JSON data.

    The reason for the duplication checks here are in case more than one player has the webhook enabled for all turns.
    That may be desirable because, for example, right now Mac users have crashes when using the webhook.
    """
    turn_time = datetime.now()
    api_logger.debug(f'JSON from Play By Cloud: {play_by_cloud_game}')
    game_name = play_by_cloud_game.value1
    time_since_last_turn = await turn_delta(game_name, turn_time)
    player = await user_service.get_user(play_by_cloud_game.value2)
    player_name = player.matrix_username or play_by_cloud_game.value2
    api_logger.debug(f"{player_name=} if it's the steam username then either no matrix username or not in database")
    turn_number = play_by_cloud_game.value3
    player_id = player.id
    await create_or_update_game(game_name, time_since_last_turn, player_id, turn_number, turn_time)

    message = f"Hey, {player_name}, it's your turn in {game_name}. The game is on turn {turn_number}"
    await api_matrix_bot.send_message(message)
    return fastapi.responses.JSONResponse(status_code=status.HTTP_201_CREATED,
                                          content={"status": "Game Created"})


@router.post('/pydt', status_code=status.HTTP_201_CREATED)
async def handle_pydt_json(pydt_game: PYDTTurnInfo):
    api_logger.debug(f'JSON from PYDT: {pydt_game}')
    game_name = pydt_game.gameName
    player = await user_service.get_user(pydt_game.userName)
    player_name = player.matrix_username or pydt_game.userName
    player_id = str(player.id)
    api_logger.debug(f"{player_name=} if it's the steam username then either no matrix username or not in database")
    turn_number = pydt_game.round
    civ_name = pydt_game.civName
    leader_name = pydt_game.leaderName
    message = f"Hey, {player_name}, {leader_name} is waiting for you to command {civ_name} in {game_name}. " \
              f"The game is on turn {turn_number}"
    await api_matrix_bot.send_message(message)
    turn_time = datetime.now()
    time_since_last_turn = await turn_delta(game_name, turn_time)
    await create_or_update_game(game_name, time_since_last_turn, player_id, turn_number, turn_time)
    return fastapi.responses.JSONResponse(status_code=status.HTTP_201_CREATED,
                                          content={"status": "Game Created"})
