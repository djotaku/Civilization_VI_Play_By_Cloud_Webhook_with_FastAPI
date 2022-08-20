from typing import Optional

import fastapi.responses
from fastapi import APIRouter, Query

from ..dependencies import (load_most_recent_games,
                            sort_games)
from ..models.api import information_models, games
from ..services.db import game_service, user_service

router = APIRouter(tags=['Information Endpoints'])


@router.get('/current_games', response_model=information_models.CurrentGames)
async def return_current_games(player_to_blame: Optional[str] = Query(None,
                                                                      title="Player to Blame",
                                                                      description="To see how many games outstanding.")):
    """Returns the dictionary containing all the games awaiting a turn.

    If a player name is passed, it will return the games that player has outstanding.

    Otherwise, it will return a list of all the games outstanding.
    """
    if player_to_blame:
        player_id = await user_service.get_user_id_from_matrix_username(player_to_blame)
        if player_id:
            current_games = await game_service.get_current_games(player_id)
        else:
            return fastapi.responses.JSONResponse(status_code=404,
                                                  content={"error": f"{player_to_blame} does not exist"})
    else:
        current_games = await game_service.get_current_games()
    print(current_games)
    games_to_return = []
    for game in current_games:
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
    return {"games": games_to_return}


@router.get('/total_number_of_games', response_model=information_models.GameCounts)
async def return_total_number_of_games():
    """Returns the total number of games the API knows about."""
    completed_games, current_games = sort_games()
    total_games = await game_service.get_total_game_count()
    current_games = await game_service.get_current_games_count()
    completed_games = await game_service.get_completed_games_count()
    return {'total_games': total_games, 'current_games': current_games,
            "completed_games": completed_games}

# TODO: add endpoints for all games and completed games
