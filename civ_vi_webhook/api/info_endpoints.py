from typing import Optional

import fastapi.responses
from fastapi import APIRouter, Query

from ..dependencies import db_model_to_game_model
from ..models.api import information_models
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
    games_to_return = await db_model_to_game_model(current_games)
    return {"games": games_to_return}


@router.get('/completed_games', response_model=information_models.CurrentGames)
async def return_completed_games():
    completed_games = await game_service.get_completed_games()
    games_to_return = await db_model_to_game_model(completed_games)
    print(games_to_return)
    return {"games": games_to_return}


@router.get('/all_games', response_model=information_models.CurrentGames)
async def get_all_games():
    all_games = await game_service.get_all_games()
    games_to_return = await db_model_to_game_model(all_games)
    return {"games": games_to_return}


@router.get('/total_number_of_games', response_model=information_models.GameCounts)
async def return_total_number_of_games():
    """Returns the total number of games the API knows about."""
    total_games = await game_service.get_total_game_count()
    current_games = await game_service.get_current_games_count()
    completed_games = await game_service.get_completed_games_count()
    return {'total_games': total_games, 'current_games': current_games,
            "completed_games": completed_games}

