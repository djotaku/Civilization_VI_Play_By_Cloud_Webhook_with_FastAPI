import fastapi.responses
from fastapi import APIRouter, Query, status, Request
import json

from civ_vi_webhook import api_logger
from ..dependencies import load_most_recent_games, dict_to_game_model
from ..models.action_models import DeletedGame, CompletedGame, Error

router = APIRouter(tags=['Action Endpoints'])


@router.delete('/delete_game', status_code=status.HTTP_200_OK, response_model=DeletedGame)
def delete_game(game_to_delete: str = Query(None,
                                            title="Game to Delete",
                                            description="The name of the game to delete")):
    """Delete the game passed to this endpoint."""
    current_games = load_most_recent_games()
    if game_to_delete not in current_games.keys():
        return fastapi.responses.JSONResponse(status_code=404,
                                              content={"error": f"{game_to_delete} not found."})
    deleted_game = current_games.pop(game_to_delete)
    with open('most_recent_games.json', 'w') as most_recent_games_file:
        json.dump(current_games, most_recent_games_file)
    api_logger.debug(f"Deleted {deleted_game}")
    deleted_response = dict_to_game_model(deleted_game)
    return {"deleted_game": deleted_response}


@router.put('/complete_game', status_code=status.HTTP_200_OK, response_model=CompletedGame,
            responses={status.HTTP_404_NOT_FOUND: {"model": Error}})
def complete_game(game_to_complete: str = Query(None,
                                                title="Game to Mark as Completed",
                                                description="The name of the game to mark as completed")):
    """Mark as completed the game passed to this endpoint."""
    current_games = load_most_recent_games()
    if game_to_complete not in current_games.keys():
        return fastapi.responses.JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                              content={"error": f"Game: {game_to_complete} not found."})
    current_games[game_to_complete]['game_completed'] = True
    api_logger.debug(f"Marked game: {game_to_complete} as completed.")
    with open('most_recent_games.json', 'w') as most_recent_games_file:
        json.dump(current_games, most_recent_games_file)
    completed_response = dict_to_game_model({f"{game_to_complete}": current_games[game_to_complete]})
    return {"completed_game": completed_response}


@router.put('/set_winner', status_code=status.HTTP_200_OK, responses={status.HTTP_404_NOT_FOUND: {"model": Error}})
async def set_winner(request: Request,
                     game: str = Query(None, title="Game",
                                       description="The name of the game to set the winner in"),
                     ):
    form_data = await request.form()
    winner = form_data['Winner']
    current_games = load_most_recent_games()
    if game not in current_games.keys():
        return fastapi.responses.JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                              content={"error": f"Game: {game} not found."})
    current_games[game]['winner'] = winner
    with open('most_recent_games.json', 'w') as most_recent_games_file:
        json.dump(current_games, most_recent_games_file)
    winner_response = dict_to_game_model({f"{game}": current_games[game]})
    return {"winner_set": winner_response}
