from typing import Optional

import fastapi.responses
from fastapi import APIRouter, Query

from ..dependencies import (dict_to_game_model, load_most_recent_games,
                            sort_games)
from ..models import information_models

router = APIRouter(tags=['Information Endpoints'])


@router.get('/current_games', response_model=information_models.CurrentGames)
def return_current_games(player_to_blame: Optional[str] = Query(None,
                                                                title="Player to Blame",
                                                                description="To see how many games outstanding.")):
    """Returns the dictionary containing the games awaiting a turn.

    If a player name is passed, it will return the games that player has outstanding.

    Otherwise, it will return a list of all the games outstanding.
    """
    current_games = load_most_recent_games()
    if player_to_blame:
        does_player_exist = any(
            player_to_blame in current_games[games].get('player_name')
            for games in current_games.keys())

        if does_player_exist:
            return {"games": [dict_to_game_model({game: game_attributes})
                              for (game, game_attributes) in current_games.items()
                              if current_games[game].get('player_name') == player_to_blame]}
        else:
            return fastapi.responses.JSONResponse(status_code=404,
                                                  content={"error": f"{player_to_blame} does not exist"})
    all_games = [dict_to_game_model({game: game_attributes}) for (game, game_attributes) in current_games.items()]
    return {"games": all_games}


@router.get('/total_number_of_games', response_model=information_models.GameCounts)
def return_total_number_of_games():
    """Returns the total number of games the API knows about."""
    all_games = load_most_recent_games()
    completed_games, current_games = sort_games()
    return {'total_games': len(all_games), 'current_games': len(current_games),
            "completed_games": len(completed_games)}
