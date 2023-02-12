import fastapi.responses
from fastapi import APIRouter, Query, Request, status

from civ_vi_webhook import api_logger

from ..dependencies import db_model_to_game_model
from ..models.api.action_models import CompletedGame, DeletedGame, Error, User
from ..models.db.user import User as DbUser
from ..services.db import game_service, user_service

router = APIRouter(tags=['Action Endpoints'])


@router.post('/add_user', status_code=status.HTTP_201_CREATED, response_model=User)
async def add_user(user: User):
    """Add a user into the database."""
    api_logger.debug(user)
    user = await DbUser.find_one(DbUser.steam_username == user.steam_username)
    if not user:
        user = await user_service.create_user(user.steam_username, maxtrix_username=user.matrix_username,
                                              index_name=user.index_name)
    return user


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
    completed_response = await db_model_to_game_model(game_to_complete)
    return {"completed_game": completed_response}


@router.put('/set_winner', status_code=status.HTTP_200_OK, responses={status.HTTP_404_NOT_FOUND: {"model": Error}})
async def set_winner(request: Request,
                     game: str = Query(None, title="Game",
                                       description="The name of the game to set the winner in"),
                     ):
    form_data = await request.form()
    winner = form_data['Winner']
    game_exists = await game_service.check_for_game(game)
    if not game_exists:
        return fastapi.responses.JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                              content={"error": f"Game: {game} not found."})
    await game_service.add_winner_to_game(game, winner)
    winner_response = await db_model_to_game_model(game)
    return {"winner_set": winner_response}
