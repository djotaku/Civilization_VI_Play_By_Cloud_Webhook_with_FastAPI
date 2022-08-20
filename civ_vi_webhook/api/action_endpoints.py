import json

import fastapi.responses
from fastapi import APIRouter, Query, Request, status

from civ_vi_webhook import api_logger

from ..dependencies import dict_to_game_model, load_most_recent_games
from ..models.api.action_models import CompletedGame, DeletedGame, Error
from ..models.api import games

from ..services.db import game_service, user_service

router = APIRouter(tags=['Action Endpoints'])


@router.delete('/delete_game', status_code=status.HTTP_200_OK, response_model=DeletedGame)
async def delete_game(game_to_delete: str = Query(None,
                                            title="Game to Delete",
                                            description="The name of the game to delete")):
    """Delete the game passed to this endpoint."""
    game_exists = await game_service.check_for_game(game_to_delete)
    if not game_exists:
        return fastapi.responses.JSONResponse(status_code=404,
                                              content={"error": f"{game_to_delete} not found."})
    game_was_deleted = await game_service.delete_game(game_to_delete)
    if game_was_deleted:
        api_logger.debug(f"Deleted {game_to_delete}")
    deleted_response = DeletedGame(deleted_game_name=game_to_delete)
    return {"deleted_game": deleted_response}


@router.put('/complete_game', status_code=status.HTTP_200_OK, response_model=CompletedGame,
            responses={status.HTTP_404_NOT_FOUND: {"model": Error}})
async def complete_game(game_to_complete: str = Query(None,
                                                title="Game to Mark as Completed",
                                                description="The name of the game to mark as completed")):
    """Mark as completed the game passed to this endpoint."""
    game_exists = await game_service.check_for_game(game_to_complete)
    if not game_exists:
        return fastapi.responses.JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                              content={"error": f"Game: {game_to_complete} not found."})
    await game_service.mark_game_completed(game_to_complete)
    api_logger.debug(f"Marked game: {game_to_complete} as completed.")
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
    completed_response = games.Game(game_name=game.game_name, game_info=game_info)
    return {"completed_game": completed_response}


@router.put('/set_winner', status_code=status.HTTP_200_OK, responses={status.HTTP_404_NOT_FOUND: {"model": Error}})
async def set_winner(request: Request,
                     game: str = Query(None, title="Game",
                                       description="The name of the game to set the winner in"),
                     ):
    form_data = await request.form()
    winner = form_data['Winner']
    current_games = load_most_recent_games()
    game_exists = await game_service.check_for_game(game)
    if not game_exists:
        return fastapi.responses.JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                              content={"error": f"Game: {game} not found."})
    await game_service.add_winner_to_game(game, winner)
    game = await game_service.get_game(game)
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
    winner_response = games.Game(game_name=game.game_name, game_info=game_info)
    return {"winner_set": winner_response}
