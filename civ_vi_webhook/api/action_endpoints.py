import fastapi.responses
from fastapi import HTTPException, APIRouter, Query, status
import json

from civ_vi_webhook import api_logger
from ..dependencies import load_most_recent_games, dict_to_game_model
from ..models.action_models import DeletedGame

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
